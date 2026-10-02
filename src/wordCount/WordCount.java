package wordCount;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

public class WordCount {

    public static void main(String[] args) throws Exception {

        // Check input and output paths
        if (args.length != 2) {
            System.err.println(
                "Usage: WordCount <input path> <output path>"
            );
            System.exit(-1);
        }

        // Create Hadoop configuration
        Configuration conf = new Configuration();

        // Create MapReduce job
        Job job = Job.getInstance(conf, "Word Count");

        // Set the main class
        job.setJarByClass(WordCount.class);

        // Set Mapper
        job.setMapperClass(WordCountMapper.class);

        // Set Reducer
        job.setReducerClass(WordCountReducer.class);

        // Mapper output types
        job.setMapOutputKeyClass(Text.class);
        job.setMapOutputValueClass(IntWritable.class);

        // Final Reducer output types
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(IntWritable.class);

        // Input path
        FileInputFormat.addInputPath(
            job,
            new Path(args[0])
        );

        // Output path
        FileOutputFormat.setOutputPath(
            job,
            new Path(args[1])
        );

        // Run the job
        System.exit(
            job.waitForCompletion(true) ? 0 : 1
        );
    }
}