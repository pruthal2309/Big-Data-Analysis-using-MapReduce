package preprocessing;

import java.io.*;
import java.util.*;

public class DataCleaner {

    public static void main(String[] args) {

        if (args.length != 2) {
            System.out.println(
                "Usage: DataCleaner <input-file> <output-file>"
            );
            return;
        }

        String inputFile = args[0];
        String outputFile = args[1];

        try (
            BufferedReader reader =
                new BufferedReader(new FileReader(inputFile));

            BufferedWriter writer =
                new BufferedWriter(new FileWriter(outputFile))
        ) {

            String line;

            while ((line = reader.readLine()) != null) {

                // Convert to lowercase
                line = line.toLowerCase();

                // Remove URLs
                line = line.replaceAll(
                    "https?://\\S+|www\\.\\S+",
                    ""
                );

                // Remove HTML tags
                line = line.replaceAll(
                    "<[^>]*>",
                    ""
                );

                // Remove punctuation and special characters
                line = line.replaceAll(
                    "[^a-z0-9\\s]",
                    " "
                );

                // Remove extra spaces
                line = line.replaceAll(
                    "\\s+",
                    " "
                ).trim();

                // Ignore empty lines
                if (!line.isEmpty()) {
                    writer.write(line);
                    writer.newLine();
                }
            }

            System.out.println(
                "Data cleaning completed successfully."
            );

            System.out.println(
                "Cleaned file: " + outputFile
            );

        } catch (IOException e) {

            System.out.println(
                "Error while cleaning data:"
            );

            e.printStackTrace();
        }
    }
}