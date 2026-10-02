package wordCount;

import java.io.IOException;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

public class WordCountMapper
        extends Mapper<LongWritable, Text, Text, IntWritable> {

    private final static IntWritable ONE = new IntWritable(1);
    private final Text word = new Text();

    @Override
    public void map(LongWritable key, Text value, Context context)
            throws IOException, InterruptedException {

        // Convert input line into String
        String line = value.toString();

        // Convert to lowercase
        line = line.toLowerCase();

        // Remove punctuation
        line = line.replaceAll("[^a-zA-Z0-9\\s]", "");

        // Split line into words
        String[] words = line.split("\\s+");

        // Emit each word with value 1
        for (String w : words) {

            if (!w.isEmpty()) {
                word.set(w);
                context.write(word, ONE);
            }
        }
    }
}