import sys
import os
import json
import threading
from datetime import datetime

class DataStorage:
    def __init__(self, target_volume_mb=500, file_size_mb=10):
        self.target_volume_mb = target_volume_mb
        self.file_size_mb = file_size_mb
        self.total_data_collected = 0
        self.file_index = 1
        self.output_folder = 'CrawledData'
        self._check_directory_exists(self.output_folder)
        self.lock = threading.Lock() #thread lock for safe/un-interrupted file writes
    
    def _check_directory_exists(self, directory):
        #ensure the directory exists, and if not, create it
        if not os.path.exists(directory):
            os.makedirs(directory)  # Create the directory if it does not exist.

    def store_data(self, processed_posts, subreddit_name):
        try:
            print(f"\nStoring data for r/{subreddit_name} - start")
            #generate unique file path within the same directory
            with self.lock:
                file_path = self._generate_file_path(subreddit_name)
                with open(file_path, 'w', encoding='utf-8') as file:
                    for post_json in processed_posts:
                        json_data = json.dumps(post_json,ensure_ascii=False,separators=(',', ':'))
                        current_file_size = sys.getsizeof(json_data)
                        self.total_data_collected += current_file_size

                        file.write(json_data + '\n') #write the post's data to file
                        #reset if the file size limit is reached
                        if self.total_data_collected >= self.file_size_mb * 1024 * 1024:
                            self.total_data_collected = 0  #reset total data collected
                            self.file_index += 1  #increment file index for new file
                            file_path = self._generate_file_path(subreddit_name)  #generate new file path
                            file = open(file_path, 'w',encoding='utf-8')  #open new file for new writes

            print(f"Saved data to {file_path}, Total Data Collected: {self.total_data_collected / 1024 / 1024} MB")
        except Exception as e:
            print(f"Failed to store data for r/{subreddit_name}: {e}")

    def _generate_file_path(self, subreddit_name):
        #include subreddit's name, timestamp and file index
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{subreddit_name}_{timestamp}_{self.file_index}.jsonl"
        return os.path.join(self.output_folder, filename)

