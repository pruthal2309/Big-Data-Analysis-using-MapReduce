package coOccurrence;

import java.io.IOException;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

public class CoOccurrenceMapper
        extends Mapper<Object, Text, Text, IntWritable> {

    private static final IntWritable ONE =
            new IntWritable(1);

    private final Text pair = new Text();

    @Override
    public void map(
            Object key,
            Text value,
            Context context)
            throws IOException, InterruptedException {

        String line = value.toString().trim();

        if (line.isEmpty()) {
            return;
        }

        String[] words = line.split("\\s+");

        for (int i = 0; i < words.length - 1; i++) {

            String word1 = words[i];
            String word2 = words[i + 1];

            // Create adjacent word pair
            pair.set(word1 + " " + word2);

            context.write(pair, ONE);
        }
    }
}