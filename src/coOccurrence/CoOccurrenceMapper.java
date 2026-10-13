package coOccurrence;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.net.URI;
import java.util.HashSet;
import java.util.Set;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

public class CoOccurrenceMapper
        extends Mapper<Object, Text, Text, IntWritable> {

    private static final IntWritable ONE =
            new IntWritable(1);

    private final Text pair = new Text();

    // Stores the Top 10 words
    private final Set<String> top10Words =
            new HashSet<>();

    @Override
    protected void setup(Context context)
            throws IOException, InterruptedException {

        // Get files distributed by Hadoop
        URI[] cacheFiles = context.getCacheFiles();

        if (cacheFiles == null || cacheFiles.length == 0) {
            throw new IOException(
                    "top10.txt was not found in Distributed Cache"
            );
        }

        String top10File = null;

        // Find top10.txt
        for (URI uri : cacheFiles) {

            String fileName =
                    new File(uri.getPath()).getName();

            if (fileName.equals("top10.txt")) {
                top10File = fileName;
                break;
            }
        }

        if (top10File == null) {
            throw new IOException(
                    "top10.txt was not found in Distributed Cache"
            );
        }

        // Read localized top10.txt
        BufferedReader reader =
                new BufferedReader(
                        new FileReader(top10File)
                );

        String line;

        while ((line = reader.readLine()) != null) {

            line = line.trim();

            if (line.isEmpty()) {
                continue;
            }

            // Expected format:
            // word frequency
            String[] parts =
                    line.split("\\s+");

            if (parts.length >= 1) {
                top10Words.add(parts[0]);
            }
        }

        reader.close();
    }

    @Override
    public void map(
            Object key,
            Text value,
            Context context)
            throws IOException, InterruptedException {

        String line =
                value.toString().trim();

        if (line.isEmpty()) {
            return;
        }

        String[] words =
                line.split("\\s+");

        for (int i = 0;
             i < words.length - 1;
             i++) {

            String word1 = words[i];
            String word2 = words[i + 1];

            // Only process pairs where the first
            // word is one of the Top 10 words.
            if (!top10Words.contains(word1)) {
                continue;
            }

            // Create adjacent word pair
            pair.set(
                    word1 + " " + word2
            );

            context.write(pair, ONE);
        }
    }
}