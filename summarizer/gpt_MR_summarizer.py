from summarizer.abstract_summarizer import AbstractSummarizer
from openai import OpenAI
import concurrent.futures
from datetime import datetime

class GPTMRSummarizer(AbstractSummarizer):
    def __init__(self, api_key: str, map_count: int, sum_reduce: bool = False) -> None:
        self.client = OpenAI(api_key=api_key)
        self.map_count = map_count
        self.sum_reduce = sum_reduce

    def summarize(self, history: str, split: str = 'count') -> str:
        '''
        Summarize using MapReduce programming model
        Map splits up text and makes concurrent API calls
        Reduce collates results and (optionally) combines with a final summarization
        '''

        chat_lists = self.parse_history(history, split)
        map_results = self.map_summarize(chat_lists)

        if self.sum_reduce:
            return self.reduce(map_results)
        else:
            # return map results as single string?
            return ''
    
    def parse_history(self, history: str, split: str) -> list:
        '''
        Split list of comments into equal portions for parallel summarization
        '''

        # extremely jank rn, will not work with more than one bot guild or channel in history dict
        # TODO get server and channel name from somewhere
        # get list of tuples (user, message)
        serv = list(history.keys())[0]
        chan = list(history[serv].keys())[0]
        messages = history[serv][chan]

        # split up messages into equal groups
        if split == 'count':
            # perform split based on message count
            chat_lists = []
            start = 0
            
            # calculations for size of each list
            avg = len(messages) // self.map_count
            rem = len(messages) % self.map_count
            
            # divvy up messages
            for i in range(self.map_count):
                chats = []

                # calc size of list
                list_size = avg + 1 if i < rem else avg

                # get slice of chat messages
                chunk = messages[start:start + list_size]
                for tup in chunk:
                    # cat user (tup[0]) and message (tup[1]) together
                    msg = tup[0] + ': ' + tup[1]
                    chats.append(msg)

                chat_lists.append(chats)

                # increment starting position
                start += list_size

            return chat_lists

        elif split == 'token':
            # TODO perform split based on token count
            pass
        
        return None
    
    def map_summarize(self, chat_lists: list) -> list:
        '''
        Perform parallel summarization over groups of messages
        '''
        summaries = ['' for _ in range(self.map_count)]

        # create concurrent threads to execute
        with concurrent.futures.ThreadPoolExecutor() as tp:
            future_prompt = {tp.submit(self.thread_summarize, chat_lists[i], i): i for i in range(len(chat_lists)) }
        
        # wait for all threads to complete
        for future in concurrent.futures.as_completed(future_prompt):
            thread_index = future_prompt[future]
            try:
                summary = future.result()
                summaries[thread_index] = summary
            except Exception as e:
                print(f'Error for index {thread_index}: {e}')

        return summaries

    def thread_summarize(self, chat_segment: list, idx: int) -> str:
        '''
        Summarize a single chat segment
        '''
        prompt = 'Summarize the key points and highlights from the chat logs into a single sentence'
        print(str(idx) + ' thread starting ' + str(datetime.now()))
        completion = self.client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': prompt},
                {'role': 'user', 'content': str(chat_segment)}
            ]
        )
        print(str(idx) + ' thread finished ' + str(datetime.now()))
        return completion.choices[0].message.content

    def reduce(self, map_results: list) -> str:
        '''
        Given results from parallel map summaries, collate into single result
        '''
        prompt = 'Summarize the key points and highlights from these chat log summaries into a single paragraph'

        completion = self.client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': prompt},
                {'role': 'user', 'content': str(map_results)}
            ]
        )
        return completion.choices[0].message.content

