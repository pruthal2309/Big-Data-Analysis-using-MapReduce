"""Inject explorer tab into dashboard.py — runs in UTF-8 mode."""
import re, sys
from collections import defaultdict

EXPLORER = r'''

# ==============================================================
# TAB 6 - SMART WORD RELATIONSHIP EXPLORER
# ==============================================================
@st.cache_data(show_spinner=False)
def build_word_index(_content_only=False):
    """Build neighbor lookup from co-occurrence file."""
    cooc_path = "WordCooccurrenceOutput/coOccurrence/cooccurrence.txt"
    stopwords = CONTENT_STOPWORDS if _content_only else STOPWORDS_NOISE_ONLY
    neighbors = defaultdict(list)
    edges = []
    try:
        with open(cooc_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.rsplit("\t", 1)
                if len(parts) != 2:
                    continue
                pair_str, count_str = parts
                try:
                    count = int(count_str.strip())
                except ValueError:
                    continue
                ws = pair_str.strip().split()
                if len(ws) != 2:
                    continue
                w1, w2 = ws[0].strip(), ws[1].strip()
                if (re.match(r"^[a-z]{2,}$", w1) and
                        re.match(r"^[a-z]{2,}$", w2) and
                        w1 not in stopwords and w2 not in stopwords and
                        w1 != w2 and count >= 5):
                    neighbors[w1].append((w2, count))
                    neighbors[w2].append((w1, count))
                    edges.append((w1, w2, count))
    except FileNotFoundError:
        pass
    for w in neighbors:
        neighbors[w].sort(key=lambda x: x[1], reverse=True)
    return dict(neighbors), edges


_CPAL = [
    "#6C63FF", "#FF6584", "#43E97B", "#F7971E",
    "#4FACFE", "#FFD200", "#B47FFF", "#38F9D7", "#FF9FBA", "#A8EDEA",
]


with tab6:
    st.markdown(
        '<div class="section-heading">'
        "\U0001f50d Smart Word Relationship Explorer"
        '<span class="badge" style="background:linear-gradient(135deg,#FF6584,#FF9FBA);color:#fff;">Interactive</span>'
        "</div>"
        '<div style="color:#9090AA;font-size:0.88rem;margin:-0.5rem 0 1.5rem 0;line-height:1.6;">'
        "Select any word to explore its co-occurrence neighbourhood &mdash; direct connections, "
        "cluster membership, and relationship strength &mdash; all from your Hadoop MapReduce output."
        "</div>",
        unsafe_allow_html=True,
    )

    with st.spinner("\U0001f517 Building word relationship index..."):
        _wi, _ae = build_word_index(_content_only=content_only)

    if not _wi:
        st.error("\u26a0\ufe0f Co-occurrence data not found or too small.")
    else:
        _vocab = sorted(_wi.keys())
        _c1, _c2, _c3 = st.columns([3, 1.5, 1.5])
        with _c1:
            _dw = ("the" if "the" in _wi else "window" if "window" in _wi else _vocab[0])
            _sel = st.selectbox(
                "\U0001f50e Choose a word to explore:",
                options=_vocab,
                index=_vocab.index(_dw),
                key="explorer_word",
            )
        with _c2:
            _mn = st.slider("Max neighbours", 5, 40, 15, key="exp_nbrs")
        with _c3:
            _dep = st.radio(
                "Graph depth", ["1-hop", "2-hop"], index=0, key="exp_depth",
                help="1-hop = direct connections. 2-hop = include neighbours-of-neighbours.",
            )

        _wlu = dict(zip(wc_df["word"], wc_df["frequency"])) if not wc_df.empty else {}
        _nbrs = _wi.get(_sel, [])[:_mn]
        _enodes = {_sel} | {n for n, _ in _nbrs}
        if _dep == "2-hop":
            for _nb, _ in _nbrs:
                _enodes |= {n for n, _ in _wi.get(_nb, [])[:8]}

        _Gego = nx.Graph()
        for _w1, _w2, _cnt in _ae:
            if _w1 in _enodes and _w2 in _enodes:
                _Gego.add_edge(_w1, _w2, weight=_cnt)
        _Gego.add_node(_sel)

        try:
            _comms = list(nx.community.greedy_modularity_communities(_Gego, weight="weight"))
        except Exception:
            _comms = [set(_Gego.nodes())]

        _nc_map = {}
        for _ci, _cm in enumerate(_comms):
            for _nd in _cm:
                _nc_map[_nd] = _ci

        def _gcol(_nd):
            return "#FFD700" if _nd == _sel else _CPAL[_nc_map.get(_nd, 0) % len(_CPAL)]

        _pos = nx.spring_layout(_Gego, k=2.8, seed=42, weight="weight", iterations=80)
        if _sel in _pos:
            _off = -_pos[_sel].copy()
            for _nd in _pos:
                _pos[_nd] = _pos[_nd] + _off

        _ews = [_Gego[u][v].get("weight", 1) for u, v in _Gego.edges()]
        _mxw = max(_ews) if _ews else 1
        _etraces = []
        for _u, _v, _ed in _Gego.edges(data=True):
            _r = _ed.get("weight", 1) / _mxw
            if _u == _sel or _v == _sel:
                _ec = "rgba(255,215,0,{:.2f})".format(0.3 + 0.5 * _r)
                _ew2 = 1.5 + 4.5 * _r
            else:
                _ec = "rgba(108,99,255,{:.2f})".format(0.1 + 0.3 * _r)
                _ew2 = 0.6 + 2.0 * _r
            _x0, _y0 = _pos[_u]
            _x1, _y1 = _pos[_v]
            _etraces.append(go.Scatter(
                x=[_x0, _x1, None], y=[_y0, _y1, None],
                mode="lines", line=dict(width=_ew2, color=_ec),
                hoverinfo="none", showlegend=False,
            ))

        _dd = dict(_Gego.degree())
        _mxf = max((_wlu.get(n, 1) for n in _Gego.nodes()), default=1)
        _nxl, _nyl, _ncl, _nsl, _ntl, _nhl = [], [], [], [], [], []
        for _nd in _Gego.nodes():
            _x, _y = _pos[_nd]
            _nxl.append(_x); _nyl.append(_y)
            _ncl.append(_gcol(_nd))
            _f = _wlu.get(_nd, 0)
            _nsl.append(52 if _nd == _sel else (14 + 28 * (_f / _mxf) ** 0.5))
            _ntl.append(_nd)
            _dw2 = next((c for nb, c in _wi.get(_sel, []) if nb == _nd), None)
            _hl = [
                "<b>{}</b>".format(_nd),
                "Frequency: {:,}".format(_f),
                "Connections: {}".format(_dd.get(_nd, 0)),
                "Cluster {}".format(_nc_map.get(_nd, 0) + 1),
            ]
            if _dw2:
                _hl.append("Co-occ with '{}': {:,}".format(_sel, _dw2))
            _nhl.append("<br>".join(_hl))

        _nt_exp = go.Scatter(
            x=_nxl, y=_nyl, mode="markers+text",
            marker=dict(size=_nsl, color=_ncl,
                        line=dict(width=2, color="#0D0D1A"), opacity=0.95),
            text=_ntl, textposition="top center",
            textfont=dict(size=10, color="#FFFFFF", family="Inter"),
            hovertext=_nhl, hoverinfo="text", showlegend=False,
        )

        _sx, _sy = _pos.get(_sel, (0, 0))
        _halo = go.Scatter(
            x=[_sx], y=[_sy], mode="markers",
            marker=dict(size=74, color="rgba(255,215,0,0.12)",
                        line=dict(width=3, color="#FFD700")),
            hoverinfo="skip", showlegend=False,
        )

        _ncl_n = len(_comms)
        _fig_exp = go.Figure(
            data=_etraces + [_halo, _nt_exp],
            layout=go.Layout(
                title=dict(
                    text="<b>'{}'</b>  &middot;  {} nodes  &middot;  {} edges  &middot;  {} cluster{}".format(
                        _sel, len(_Gego.nodes()), len(_Gego.edges()),
                        _ncl_n, "s" if _ncl_n != 1 else ""),
                    font=dict(size=16, color="#FFFFFF", family="Inter"), x=0.01,
                ),
                paper_bgcolor="#0D0D1A", plot_bgcolor="#0D0D1A", height=650,
                margin=dict(l=10, r=10, t=58, b=10),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                hovermode="closest", font=dict(family="Inter", color="#AAAACC"),
            )
        )

        _gcol2, _scol = st.columns([2.6, 1])

        with _gcol2:
            st.plotly_chart(_fig_exp, width="stretch")
            _leg = ""
            for _ci, _cm in enumerate(_comms[:8]):
                _cc = _CPAL[_ci % len(_CPAL)]
                _tm = sorted(_cm, key=lambda n: _wlu.get(n, 0), reverse=True)[:4]
                _leg += (
                    '<span style="display:inline-flex;align-items:center;gap:5px;'
                    'background:rgba(255,255,255,0.04);border:1px solid {}44;'
                    'border-radius:8px;padding:4px 10px;margin:4px 4px 0 0;font-size:0.78rem;">'
                    '<span style="width:10px;height:10px;border-radius:50%;background:{};'
                    'display:inline-block;flex-shrink:0;"></span>'
                    '<b style="color:{}">C{}</b>: '
                    '<span style="color:#AAAACC">{}</span></span>'
                ).format(_cc, _cc, _cc, _ci + 1, ", ".join(_tm))
            st.markdown(
                '<div style="margin-top:0.6rem;">{}</div>'.format(_leg),
                unsafe_allow_html=True,
            )

        with _scol:
            _sf = _wlu.get(_sel, 0)
            _sd = _dd.get(_sel, 0)
            _sc2 = _nc_map.get(_sel, 0)
            _scc = _CPAL[_sc2 % len(_CPAL)]
            st.markdown(
                '<div style="background:linear-gradient(135deg,rgba(255,215,0,0.10),'
                'rgba(108,99,255,0.08));border:1px solid rgba(255,215,0,0.3);'
                'border-radius:16px;padding:1.3rem;margin-bottom:1rem;">'
                '<div style="font-size:0.68rem;color:rgba(255,215,0,0.75);text-transform:uppercase;'
                'letter-spacing:0.1em;font-weight:700;margin-bottom:0.3rem;">Selected Word</div>'
                '<div style="font-size:1.9rem;font-weight:800;color:#FFD700;margin-bottom:0.8rem;'
                'word-break:break-all;">{}</div>'
                '<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;">'
                '<div style="background:rgba(0,0,0,0.25);border-radius:10px;padding:0.55rem;text-align:center;">'
                '<div style="font-size:1.1rem;font-weight:800;color:#FFFFFF;">{}</div>'
                '<div style="font-size:0.6rem;color:#8888AA;text-transform:uppercase;">Freq</div></div>'
                '<div style="background:rgba(0,0,0,0.25);border-radius:10px;padding:0.55rem;text-align:center;">'
                '<div style="font-size:1.1rem;font-weight:800;color:#FFFFFF;">{}</div>'
                '<div style="font-size:0.6rem;color:#8888AA;text-transform:uppercase;">Edges</div></div>'
                '<div style="background:rgba(0,0,0,0.25);border-radius:10px;padding:0.55rem;text-align:center;">'
                '<div style="font-size:1.1rem;font-weight:800;color:{};">C{}</div>'
                '<div style="font-size:0.6rem;color:#8888AA;text-transform:uppercase;">Cluster</div></div>'
                '<div style="background:rgba(0,0,0,0.25);border-radius:10px;padding:0.55rem;text-align:center;">'
                '<div style="font-size:1.1rem;font-weight:800;color:#FFFFFF;">{}</div>'
                '<div style="font-size:0.6rem;color:#8888AA;text-transform:uppercase;">Nodes</div></div>'
                '</div></div>'.format(
                    _sel, "{:,}".format(_sf), _sd,
                    _scc, _sc2 + 1, len(_Gego.nodes())
                ),
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div style="font-size:0.82rem;font-weight:700;color:#B0AAFF;'
                'margin:0.2rem 0 0.5rem 0;">'
                "\U0001f517 Strongest Connections</div>",
                unsafe_allow_html=True,
            )
            _dnbrs = _wi.get(_sel, [])[:15]
            _tc = _dnbrs[0][1] if _dnbrs else 1
            for _rk, (_nb, _ct) in enumerate(_dnbrs, 1):
                _nf = _wlu.get(_nb, 0)
                _bp = int(100 * _ct / _tc) if _tc > 0 else 0
                _nbc = _CPAL[_nc_map.get(_nb, 0) % len(_CPAL)]
                st.markdown(
                    '<div style="background:rgba(255,255,255,0.03);'
                    'border:1px solid rgba(255,255,255,0.06);'
                    'border-radius:9px;padding:0.45rem 0.65rem;margin-bottom:0.32rem;">'
                    '<div style="display:flex;justify-content:space-between;align-items:center;">'
                    '<div style="font-weight:700;color:{};font-size:0.84rem;">#{} {}</div>'
                    '<div style="font-size:0.72rem;color:#43E97B;font-weight:700;">{}</div></div>'
                    '<div style="background:rgba(255,255,255,0.04);border-radius:4px;'
                    'height:4px;margin-top:0.28rem;overflow:hidden;">'
                    '<div style="background:{};width:{}%;height:100%;border-radius:4px;"></div></div>'
                    '<div style="font-size:0.65rem;color:#555577;margin-top:0.14rem;">freq: {}</div>'
                    '</div>'.format(
                        _nbc, _rk, _nb, "{:,}".format(_ct),
                        _nbc, _bp, "{:,}".format(_nf)
                    ),
                    unsafe_allow_html=True,
                )
            if not _dnbrs:
                st.info("No direct connections found for this word.")

            st.markdown(
                '<div style="font-size:0.82rem;font-weight:700;color:#B0AAFF;'
                'margin:0.8rem 0 0.5rem 0;">'
                "\U0001fae7 Cluster Breakdown</div>",
                unsafe_allow_html=True,
            )
            for _ci, _cm in enumerate(_comms):
                _cc = _CPAL[_ci % len(_CPAL)]
                _tm = sorted(_cm, key=lambda n: _wlu.get(n, 0), reverse=True)[:5]
                st.markdown(
                    '<div style="background:rgba(255,255,255,0.02);'
                    'border-left:3px solid {};border-radius:0 8px 8px 0;'
                    'padding:0.45rem 0.7rem;margin-bottom:0.32rem;">'
                    '<div style="font-size:0.72rem;font-weight:700;color:{};">'
                    'Cluster {} <span style="color:#555577;font-weight:400;">({} words)</span></div>'
                    '<div style="font-size:0.68rem;color:#AAAACC;margin-top:0.12rem;">{}</div>'
                    '</div>'.format(
                        _cc, _cc, _ci + 1, len(_cm),
                        " &middot; ".join(_tm)
                    ),
                    unsafe_allow_html=True,
                )

        _sn = _dnbrs[0][0] if _dnbrs else "N/A"
        _sc3 = _dnbrs[0][1] if _dnbrs else 0
        st.markdown(
            '<div class="insight-strip" style="margin-top:1.2rem;">'
            '<div class="insight-item">\U0001f31f '
            "<span>The word <b style=\"color:#FFD700;\">'{}' </b>"
            "co-occurs most strongly with <b style=\"color:#43E97B;\">{}</b>"
            " ({:,}&times;), indicating a tight semantic relationship in the corpus.</span></div>"
            '<div class="insight-item">\U0001fae7 '
            "<span>NetworkX detected <b style=\"color:#B0AAFF;\">{} cluster{}</b>"
            " using greedy modularity maximisation &mdash; each cluster groups words"
            " that frequently appear together in the same context window.</span></div>"
            '<div class="insight-item">\u2b55 '
            "<span><b style=\"color:#FFD700;\">Gold node + ring</b> = selected word &nbsp;"
            "<b style=\"color:#6C63FF;\">Colored nodes</b> = cluster &nbsp;"
            "<b>Brighter edges</b> = higher co-occurrence. "
            "Hover any node for full statistics. Drag to rearrange.</span></div>"
            "</div>".format(
                _sel, _sn, _sc3,
                _ncl_n, "s" if _ncl_n != 1 else ""
            ),
            unsafe_allow_html=True,
        )

'''

# Read current file
with open("dashboard.py", "r", encoding="utf-8") as f:
    content = f.read()

# Locate the footer section start (dashes line before "# FOOTER")
idx_footer = content.find("# FOOTER\n")
# Step back to find the dashes comment line before it
insert_at = content.rfind("\n# ", 0, idx_footer)
insert_at += 1   # skip the leading \n, insert before the "# ---" line

# Insert explorer code
new_content = content[:insert_at] + EXPLORER + "\n" + content[insert_at:]

with open("dashboard.py", "w", encoding="utf-8") as f:
    f.write(new_content)

# Verify
with open("dashboard.py", "r", encoding="utf-8") as f:
    v = f.read()

ok_wi  = "build_word_index" in v
ok_t6  = "with tab6:" in v
ok_tab = "tab6 = st.tabs" in v or 'tab6 = st.tabs' in v
with open("_inject_result.txt", "w") as f:
    f.write(f"build_word_index: {ok_wi}\nwith tab6: {ok_t6}\nLine count: {v.count(chr(10))}\n")
