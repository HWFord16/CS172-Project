import sys
import os
import json

class DataStorage:
    def __init__(self, target_volume_mb=500, file_size_mb=10):
        self.target_volume_mb = target_volume_mb
        self.file_size_mb = file_size_mb
        self.total_data_collected = 0
        self.file_index = 1
        self.output_folder = 'CrawledData'
        self._check_directory_exists(self.output_folder)

    def store_data(self, processed_posts, subreddit_name):
        for post_json in processed_posts:
            current_file_size = sys.getsizeof(post_json)  #calculate post in bytes per post
            self.total_data_collected += current_file_size #update total size
            
            #check the current post size doesnt exceed file size limit
            if current_file_size >= self.file_size_mb * 1024 * 1024:
                self._write_to_file(processed_posts, subreddit_name) #write all processed post to file prior to limit
                processed_posts = [] #reset the processed posts

            #check total limit size and break out of loop if exceeded
            if self.total_data_collected >= self.target_volume_mb * 1024 * 1024:
                break
        # check for any remaining processed post after loop
        if processed_posts:
            self._write_to_file(processed_posts, subreddit_name)

    #write processed post to file
    def _write_to_file(self, data, subreddit_name):
        #format the file path w/subreddit name & index
        file_path = os.path.join(self.output_folder, f"{subreddit_name}_{self.file_index}.jsonl") 
        with open(file_path, 'w') as file: #convert each dictionary to a JSON string and write it to file.
            file.writelines([json.dumps(post) + '\n' for post in data])
        self.file_index += 1  #update index
        #return total size posts collected and saved
        print(f"Saved {file_path}, Total Data Collected: {self.total_data_collected / 1024 / 1024} MB")

    def _check_directory_exists(self, directory):
        #ensure the directory exists, and if not, create it
        if not os.path.exists(directory):
            os.makedirs(directory)  # Create the directory if it does not exist.