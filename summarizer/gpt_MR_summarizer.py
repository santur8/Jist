from summarizer.abstract_summarizer import AbstractSummarizer
import openai
import concurrent.futures


class GPTMRSummarizer(AbstractSummarizer):
    def __init__(self, api_key: str, map_count: int) -> None:
        openai.api_key = api_key
        self.map_count = map_count

    def summarize(self, history: str, split: str = 'count') -> str:
        '''
        Summarize using MapReduce programming model
        Map splits up text and makes concurrent API calls
        Reduce collates results and (optionally) combines with a final summarization
        '''

        chat_lists = self.parse_history(history, split)
        map_results = self.map_summarize(chat_lists)
        for res in map_results:
            print(res)
            print()


        return ""
    
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
            future_prompt = {tp.submit(self.thread_summarize, chat_lists[i]): i for i in range(len(chat_lists)) }
        
        # wait for all threads to complete
        for future in concurrent.futures.as_completed(future_prompt):
            thread_index = future_prompt[future]
            try:
                summary = future.result()
                summaries[thread_index] = summary
            except Exception as e:
                print(f"Error for index {thread_index}: {e}")

        return summaries

    def thread_summarize(self, chat_segment: list) -> str:
        '''
        Summarize a single chat segment
        '''
        return 'pass'
        prompt = 'Summarize the key points and highlights from the chat logs'
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": chat_segment}
            ]
        )
        return completion.choices[0].message.content



    # def summarize(self, history: str) -> str:
    #     completion = openai.ChatCompletion.create(
    #         model="gpt-3.5-turbo",
    #         messages=[
    #             {"role": "system", "content": "You are an assistant that summarizes chat historys to help user grasp recent news in an online chat room."},
    #             {"role": "user", "content": history}
    #         ]
    #     )
    #     return completion.choices[0].message.content

'''
response = openai.Completion.create(
            model="gpt-3.5-turbo",
            prompt=prompt,
            max_tokens=50
        )
'''
