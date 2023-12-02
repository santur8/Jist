from typing import Literal
from .json_summarizer import JsonSummarizer, Json
from openai import OpenAI
import concurrent.futures
import tiktoken
from datetime import datetime
import queue
from loguru import logger

TOKEN_LIMIT = 4096-50  # token limit for GPT 3.5 Turbo, minus some room for prompt

summary_queue = queue.Queue(maxsize=10)
map_results = [''] * 10

class GPTMRSummarizer(JsonSummarizer):
    def __init__(self, api_key: str, map_count: int, sum_reduce: bool = False) -> None:
        self.client = OpenAI(api_key=api_key)
        self.map_count = map_count
        self.sum_reduce = sum_reduce
        self.encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
        logger.info('initialized openai client')

    def summarize(self, history: Json, split: Literal['count'] | Literal['token'] = 'token') -> str:
        '''
        Summarize using MapReduce programming model
        Map splits up text and makes concurrent API calls
        Reduce collates results and (optionally) combines with a final summarization
        Assumes the following JSON input format:
            dictionary of servers
                containing dictionary of channels 
                    containing list of messages
        { 
            server1: {
                channel1: {
                    ['user1: message1', 'user2: message2', 'user1: message3', ...]
                },
                channel2: {
                    ['user1: message1', 'user2: message2', 'user1: message3', ...]
                }, ...
            }, ...
        }
        '''
        summary = ''
        for server in history.keys():
            for channel in history[server].keys():
                logger.info(f'map phase for {server}: {channel}')
                self.parse_history(history[server][channel], split='token')
                self.map_summarize()
                reduce_results = server + ': ' + channel + ':\n'
                if self.sum_reduce:
                    logger.info(f'reduce phase for {server}: {channel}')
                    reduce_results += self.reduce()
                else:
                    for res in map_results:
                        reduce_results += res + '\n'
                summary += reduce_results + '\n'
        
        return summary
    
    def parse_history(self, messages: list, split: Literal['count'] | Literal['token']):
        '''
        Split list of chats into equal portions for parallel summarization
        '''

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
                # calc size of list
                list_size = avg + 1 if i < rem else avg

                # get slice of chat messages
                chunk = messages[start:start + list_size]
                chat_lists.append(chunk)

                # increment starting position
                start += list_size

            return chat_lists

        elif split == 'token':
            # TODO perform split based on token count
            chat_list = []
            start = 0

            chunk_size = TOKEN_LIMIT
            chunk = ''

            for message in messages:
                token_count = len(self.encoding.encode(message + ', '))
                
                if token_count < chunk_size:
                    # append to current chunk
                    chunk += message
                    chunk += ', '
                    chunk_size -= token_count
                else:
                    # current chunk of maximum size
                    # append current chunk to list
                    chat_list.append(chunk)
                    chunk = ''
                    chunk_size = TOKEN_LIMIT
                    
                    # start new chunk
                    chunk += message
                    chunk += ', '
                    chunk_size -= token_count

            
            # final append for last chunk
            chat_list.append(chunk)

            if len(chat_list) >= 10:
                return

            for i in range(0, len(chat_list)):
                tup = (i, chat_list[i])
                summary_queue.put_nowait(tup)

        return
    
    def map_summarize(self):
        '''
        Perform parallel summarization over groups of messages
        '''
        # create concurrent threads to execute
        with concurrent.futures.ThreadPoolExecutor() as tp:
            future_prompt = {tp.submit(self.thread_summarize) for _ in range(self.map_count) }
        
        # wait for all threads to complete
        for future in concurrent.futures.as_completed(future_prompt):
            try:
                assert future.done()
            except Exception as e:
                logger.error(f'Error for future: {e}')

        return

    def thread_summarize(self) -> (int, str):
        '''
        Summarize a single chat segment
        '''
        prompt = 'Summarize the key points and highlights from the chat logs into a single, concise sentence:'
        while True:
            try:
                tup = summary_queue.get_nowait()
                idx = tup[0]
                chat_segment = tup[1]

                logger.info(f'summarizing chunk {idx}')
                completion = self.client.chat.completions.create(
                    model='gpt-3.5-turbo',
                    messages=[
                        {'role': 'system', 'content': prompt},
                        {'role': 'user', 'content': str(chat_segment)}
                    ]
                )
                logger.info(f'chunk {idx} finished')
                assert completion.choices[0].message.content is not None
                map_results[idx] = completion.choices[0].message.content
            except queue.Empty:
                break  # Queue is empty, exit the loop
        return

    def reduce(self) -> str:
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
        assert completion.choices[0].message.content is not None
        return completion.choices[0].message.content

