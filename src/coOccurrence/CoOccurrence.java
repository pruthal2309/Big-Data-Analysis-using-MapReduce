package coOccurrence;

import java.net.URI;

import org.apache.hadoop.conf.Configuration; // loads Hadoop configuration Setting
import org.apache.hadoop.fs.FileSystem; // Interacts with HDFS 
import org.apache.hadoop.fs.Path; // represents ip, op and file paths.

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;

import org.apache.hadoop.mapreduce.Job;

import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

public class CoOccurrence {

    public static void main(String[] args)
        throws Exception {
                if (args.length != 3) {System.err.println("Usage: CoOccurrence <input> <output> <top10>");
                System.exit(2);
        }

        Configuration conf = new Configuration();

        Job job =
                Job.getInstance(
                    conf,
                    "Word Co-occurrence"
                );

        job.setJarByClass(CoOccurrence.class);

        job.setMapperClass(
                CoOccurrenceMapper.class
        );

        job.setReducerClass(
                CoOccurrenceReducer.class
        );

        job.setOutputKeyClass(Text.class);

        job.setOutputValueClass(
                IntWritable.class
        );

        // Input HDFS path
        FileInputFormat.addInputPath(
                job,
                new Path(args[0])
        );

        // Output HDFS path
        FileOutputFormat.setOutputPath(
                job,
                new Path(args[1])
        );

        // Get the Top 10 file from HDFS
        FileSystem fs =
                FileSystem.get(conf);

        Path top10Path =
                new Path(args[2]);

        // Distribute top10.txt to every mapper
        job.addCacheFile(
                fs.makeQualified(top10Path).toUri()
        );

        System.exit(
            job.waitForCompletion(true)
                ? 0
                : 1
        );
    }
}