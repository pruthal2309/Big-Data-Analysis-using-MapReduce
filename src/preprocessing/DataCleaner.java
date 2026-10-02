package preprocessing;

import java.io.*;
import java.nio.file.*;

public class DataCleaner {

    public static void main(String[] args) {

        if (args.length != 2) {
            System.out.println(
                "Usage: DataCleaner <input-folder> <output-folder>"
            );
            return;
        }

        String inputFolder = args[0];
        String outputFolder = args[1];

        File inputDir = new File(inputFolder);
        File outputDir = new File(outputFolder);

        // Check input directory
        if (!inputDir.exists() || !inputDir.isDirectory()) {
            System.out.println(
                "Input folder does not exist: " + inputFolder
            );
            return;
        }

        // Create output directory if it does not exist
        if (!outputDir.exists()) {
            outputDir.mkdirs();
        }

        File[] files = inputDir.listFiles();

        if (files == null || files.length == 0) {
            System.out.println("No files found in input folder.");
            return;
        }

        int processedFiles = 0;

        for (File inputFile : files) {

            // Process only .txt files
            if (!inputFile.isFile() ||
                !inputFile.getName().toLowerCase().endsWith(".txt")) {
                continue;
            }

            String inputFileName = inputFile.getName();

            // Example:
            // ArticleBooks1.txt
            // becomes:
            // CleanedArticleBooks1.txt

            String outputFileName =
                "Cleaned" + inputFileName;

            File outputFile =
                new File(outputDir, outputFileName);

            System.out.println(
                "Processing: " + inputFileName
            );

            cleanFile(inputFile, outputFile);

            processedFiles++;

            System.out.println(
                "Created: " + outputFileName
            );

            System.out.println("--------------------------------");
        }

        System.out.println();
        System.out.println(
            "Data cleaning completed successfully."
        );

        System.out.println(
            "Total files processed: " + processedFiles
        );
    }


    private static void cleanFile(
            File inputFile,
            File outputFile) {

        try (
            BufferedReader reader =
                new BufferedReader(
                    new FileReader(inputFile)
                );

            BufferedWriter writer =
                new BufferedWriter(
                    new FileWriter(outputFile)
                )
        ) {

            String line;

            while ((line = reader.readLine()) != null) {

                // Convert text to lowercase
                line = line.toLowerCase();

                // Remove URLs
                line = line.replaceAll(
                    "https?://\\S+|www\\.\\S+",
                    " "
                );

                // Remove HTML tags
                line = line.replaceAll(
                    "<[^>]*>",
                    " "
                );

                // Remove punctuation and special characters
                line = line.replaceAll(
                    "[^a-z0-9\\s]",
                    " "
                );

                // Remove extra whitespace
                line = line.replaceAll(
                    "\\s+",
                    " "
                ).trim();

                // Write only non-empty lines
                if (!line.isEmpty()) {

                    writer.write(line);
                    writer.newLine();
                }
            }

        } catch (IOException e) {

            System.out.println(
                "Error processing file: "
                + inputFile.getName()
            );

            e.printStackTrace();
        }
    }
}