package TopN;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;

import java.util.PriorityQueue;

public class TopNWords {

    // Class to store a word and its frequency
    static class WordFrequency {

        String word;
        int frequency;

        WordFrequency(String word, int frequency) {
            this.word = word;
            this.frequency = frequency;
        }
    }

    public static void main(String[] args) {

        if (args.length != 2) {

            System.out.println(
                "Usage: java topN.TopicNWords <input-file> <output-file>"
            );

            System.exit(1);
        }

        String inputFile = args[0];
        String outputFile = args[1];

        // Min-heap.
        // The word with the smallest frequency stays at the top.
        PriorityQueue<WordFrequency> minHeap =
            new PriorityQueue<>(
                (a, b) -> Integer.compare(a.frequency, b.frequency)
            );

        try {

            BufferedReader reader =
                new BufferedReader(
                    new FileReader(inputFile)
                );

            String line;

            while ((line = reader.readLine()) != null) {

                line = line.trim();

                if (line.isEmpty()) {
                    continue;
                }

                // Word Count output format:
                // word    frequency
                String[] parts = line.split("\\s+");

                if (parts.length < 2) {
                    continue;
                }

                String word = parts[0];

                int frequency;

                try {
                    frequency = Integer.parseInt(parts[1]);
                } catch (NumberFormatException e) {
                    continue;
                }

                WordFrequency wf =
                    new WordFrequency(word, frequency);

                minHeap.offer(wf);

                // Keep only Top 10
                if (minHeap.size() > 10) {
                    minHeap.poll();
                }
            }

            reader.close();

            // Store results temporarily
            WordFrequency[] topWords =
                new WordFrequency[minHeap.size()];

            int index = topWords.length - 1;

            while (!minHeap.isEmpty()) {

                topWords[index] = minHeap.poll();

                index--;
            }

            // Write output
            PrintWriter writer =
                new PrintWriter(
                    new FileWriter(outputFile)
                );

            writer.println("Top 10 Words");
            writer.println("====================");

            for (int i = 0; i < topWords.length; i++) {

                writer.println(
                    (i + 1)
                    + ". "
                    + topWords[i].word
                    + "\t"
                    + topWords[i].frequency
                );
            }

            writer.close();

            // Display results
            System.out.println();
            System.out.println("======================================");
            System.out.println("         TOP 10 WORDS");
            System.out.println("======================================");

            for (int i = 0; i < topWords.length; i++) {

                System.out.println(
                    (i + 1)
                    + ". "
                    + topWords[i].word
                    + " -> "
                    + topWords[i].frequency
                );
            }

            System.out.println("======================================");
            System.out.println();
            System.out.println(
                "Top 10 result saved to: " + outputFile
            );

        } catch (IOException e) {

            System.err.println(
                "Error reading/writing file:"
            );

            e.printStackTrace();

            System.exit(1);
        }
    }
}