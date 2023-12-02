from transformers import AutoTokenizer
import requests

def num_tokens_from_messages_codellama(messages, max_length):
  model="codellama/CodeLlama-34b-Instruct-hf"
  tokenizer = AutoTokenizer.from_pretrained(model)
  """Returns the number of tokens used by a list of messages."""
  # tokenizer = AutoTokenizer.from_pretrained(model)
  num_tokens = 0
  truncated_messages = []
  for message in messages:
      num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
      truncated_message = message.copy()
      for key, value in message.items():
          tokenized_message = tokenizer(value,truncation=True,return_tensors="pt",max_length = max_length)
          token_length = tokenized_message['input_ids'].shape[1]
          if num_tokens + token_length > max_length:
              # Truncate the value to fit within the token limit
              remaining_tokens = max_length - num_tokens
              truncated_value = tokenizer.decode(tokenized_message['input_ids'][0, :remaining_tokens])
              truncated_message[key] = truncated_value
              truncated_message["role"] = message.get("role", "user")
              truncated_messages.append(truncated_message)
              return truncated_messages, max_length
          num_tokens += tokenized_message['input_ids'].shape[1]
          if key == "name":  # if there's a name, the role is omitted
              num_tokens += -1  # role is always required and always 1 token
  num_tokens += 2  # every reply is primed with <im_start>assistant
  return [], num_tokens


def llama_meeting_analytics(transcription):
    model="codellama/CodeLlama-34b-Instruct-hf"
    tokenizer = AutoTokenizer.from_pretrained(model)

    url = "https://api.endpoints.anyscale.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer esecret_3mwa8mkdz5p8edi3bkzju7jsyq"
    }

    data = {
        "model": "codellama/CodeLlama-34b-Instruct-hf",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that will help me answer four seperate questions about the meeting transcript I will provide: \
            Question 1: You are a highly skilled AI trained in language comprehension and summarization. I would like you to read the meeting transcript provided and summarize it into a concise abstract paragraph. \
            Aim to retain the most important points, providing a coherent and readable summary that could help a person understand the main points of the discussion without needing to read the entire text. \
            Please avoid unnecessary details or tangential points. \
            Question 2: You are a proficient AI with a specialty in distilling meeting transcripts into topics and determining participant engagement statistics. \
                  1. First, based on the following text, identify and list the main topics that were discussed. These should be the most important ideas, findings, or topics crucial to the essence of the discussion. \
                     Limit these topic descriptions to eight or fewer words. In addition, determine the percentage of the entire meeting devoted to each topic and put that in parentheses.  Be sure to include specific numbers to \
                     express the percentage of the entire meeting devoted to each topic. \
                  2. Second, evaluate each person who partipated in the meeting discussion using the following criteria: \
                      a. Speaking Time: Compute the percentage of words each participant contributed to the discussion. \
                      b. Interactions: Count the number of times each team member interacts with others during the meeting. This includes asking questions, responding to others, or initiating discussions. \
                  Please provide this output in a comma-seperated format that lists the contributions for each participant including their speaking time percentage & interaction count.  Be sure to include specific numbers to \
                  express speaking time percentage & interaction count for each participant and that the speaking time percentages add up to 100%. \
            Question 3: You are a proficient AI with a specialty in analyzing conversations and extracting action items for each meeting participant. \
                     Please review the text and identify key tasks, assignments, or actions that were agreed upon or mentioned as needing to be done. \
                     These could be tasks assigned to specific individuals, or general actions that the group has decided to take. \
                     Please provide a bulleted list of action items seperated into sections by participant; First specify the participant  who owns each action item followed by a colon then the action item description. \
                     Be sure to refer to the participants by their speaker alias from the meeting transcript as opposed to their name. \
                     Please make sure that your responses avoid repeating the same points multiple times, remain clear and concise, and include \
                     specific numbers to express each participant's # of action items in parentheses in each block of action items. \
            Question 4: As an AI with expertise in language and emotion analysis, your task is to analyze the sentiment of the following text and label it with one of the following 13 categories: \
                Productive, Collaborative, Constructive, Efficient, Professional, Innovative, Unproductive, Chaotic, Argumentative, Tense, Inefficient, Informational, Standard. \
                Be sure to limit your output to a 1 word answer using one of the 13 words listed above considering the overall tone of the discussion, the emotion conveyed by the language used, and the context in which words and phrases are used. \
            \
            Please provide seperate answers for each of the above questions that are easily discernable from each other."},
            {"role": "user", "content": "Here is the meeting transcript: " + transcription}
        ],
        "temperature": 0.0,
        "max_tokens": 1500
    }

    messages = data['messages']
    truncated_messages, input_tokens = num_tokens_from_messages_codellama(messages, tokenizer, 14500)

    if len(truncated_messages) > 0:
        data = {
        "model": "codellama/CodeLlama-34b-Instruct-hf",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that will help me answer four seperate questions about the meeting transcript I will provide: \
            Question 1: You are a highly skilled AI trained in language comprehension and summarization. I would like you to read the meeting transcript provided and summarize it into a concise abstract paragraph. \
            Aim to retain the most important points, providing a coherent and readable summary that could help a person understand the main points of the discussion without needing to read the entire text. \
            Please avoid unnecessary details or tangential points. \
            Question 2: You are a proficient AI with a specialty in distilling meeting transcripts into topics and determining participant engagement statistics. \
                  1. First, based on the following text, identify and list the main topics that were discussed. These should be the most important ideas, findings, or topics crucial to the essence of the discussion. \
                     Limit these topic descriptions to eight or fewer words. In addition, determine the percentage of the entire meeting devoted to each topic and put that in parentheses.  Be sure to include specific numbers to \
                     express the percentage of the entire meeting devoted to each topic. \
                  2. Second, evaluate each person who partipated in the meeting discussion using the following criteria: \
                      a. Speaking Time: Compute the percentage of words each participant contributed to the discussion. \
                      b. Interactions: Count the number of times each team member interacts with others during the meeting. This includes asking questions, responding to others, or initiating discussions. \
                  Please provide this output in a comma-seperated format that lists the contributions for each participant including their speaking time percentage & interaction count.  Be sure to include specific numbers to \
                  express speaking time percentage & interaction count for each participant and that the speaking time percentages add up to 100%. \
            Question 3: You are a proficient AI with a specialty in analyzing conversations and extracting action items for each meeting participant. \
                     Please review the text and identify key tasks, assignments, or actions that were agreed upon or mentioned as needing to be done. \
                     These could be tasks assigned to specific individuals, or general actions that the group has decided to take. \
                     Please provide a bulleted list of action items seperated into sections by participant; First specify the participant  who owns each action item followed by a colon then the action item description. \
                     Be sure to refer to the participants by their speaker alias from the meeting transcript as opposed to their name. \
                     Please make sure that your responses avoid repeating the same points multiple times, remain clear and concise, and include \
                     specific numbers to express each participant's # of action items in parentheses in each block of action items. \
            Question 4: As an AI with expertise in language and emotion analysis, your task is to analyze the sentiment of the following text and label it with one of the following 13 categories: \
                Productive, Collaborative, Constructive, Efficient, Professional, Innovative, Unproductive, Chaotic, Argumentative, Tense, Inefficient, Informational, Standard. \
                Be sure to limit your output to a 1 word answer using one of the 13 words listed above considering the overall tone of the discussion, the emotion conveyed by the language used, and the context in which words and phrases are used. \
            \
            Please provide seperate answers for each of the above questions that are easily discernable from each other."},
            {"role": "user", "content": "Here is the meeting transcript: " + truncated_messages[0]['content']}], "temperature": 0.0, "max_tokens": 1500}

    if input_tokens <= 14500:
      # try:
      start_time = time.time()
      response = requests.post(url, headers=headers, json=data, timeout=1000)
      end_time = time.time()
      response_time = end_time - start_time
      model_output = response.json()['choices'][0]['message']['content']
      messages = [{"role": "system", "content": model_output}]
      truncated_messages, output_tokens = num_tokens_from_messages_codellama(messages, tokenizer, 14500)
      return input_tokens, output_tokens, response.json()['choices'][0]['message']['content'], response_time
      # except:
      #   return input_tokens, 0, 'No Response Generated -- API Request Time-out (Took > 200 s to respond)', 200

    else:
      return input_tokens, 0, 'No Response Generated -- # of Input Tokens Exceeds 16000', 0
    

def qa_extraction_llama(question, transcription):

    model="codellama/CodeLlama-34b-Instruct-hf"
    tokenizer = AutoTokenizer.from_pretrained(model)

    url = "https://api.endpoints.anyscale.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer esecret_3mwa8mkdz5p8edi3bkzju7jsyq"
    }

    data = {
        "model": "codellama/CodeLlama-34b-Instruct-hf",
        "messages": [
            {"role": "system", "content": "You are a highly skilled AI trained in language comprehension and summarization. \
            I would like you to read the meeting transcript provided and use the information contained in it to answer questions. \
            Please make sure that your responses: \
            1. Provide answers to the users questions clearly and concisely \
            2. Avoid repeating the same points multiple times. \
            3. Use a variety of formats and descriptions to present the key points. \
            Feel free to use bullet points, paraphrases, and varying levels of detail to summarize the essential content comprehensively."},
            {"role": "user", "content": transcription},
            {"role": "user", "content": question}]
            ,"temperature": 0.0}

    messages = data['messages']
    truncated_messages, input_tokens = num_tokens_from_messages_codellama(messages, tokenizer, 15800)

    if len(truncated_messages) > 0:
        data = {
        "model": "codellama/CodeLlama-34b-Instruct-hf",
        "messages": [
            {"role": "system", "content": "You are a highly skilled AI trained in language comprehension and summarization. \
            I would like you to read the meeting transcript provided and use the information contained in it to answer questions. \
            Please make sure that your responses: \
            1. Provide answers to the users questions clearly and concisely \
            2. Avoid repeating the same points multiple times. \
            3. Use a variety of formats and descriptions to present the key points. \
            Feel free to use bullet points, paraphrases, and varying levels of detail to summarize the essential content comprehensively."},
            {"role": "user", "content": truncated_messages[0]['content']},
            {"role": "user", "content": question}]
            ,"temperature": 0.0}

    else:
        data = {
        "model": "codellama/CodeLlama-34b-Instruct-hf",
        "messages": [
            {"role": "system", "content": "You are a highly skilled AI trained in language comprehension and summarization. \
            I would like you to read the meeting transcript provided and use the information contained in it to answer questions. \
            Please make sure that your responses: \
            1. Provide answers to the users questions clearly and concisely \
            2. Avoid repeating the same points multiple times. \
            3. Use a variety of formats and descriptions to present the key points. \
            Feel free to use bullet points, paraphrases, and varying levels of detail to summarize the essential content comprehensively."},
            {"role": "user", "content": transcription},
            {"role": "user", "content": question}]
            ,"temperature": 0.0}

    try:
      start_time = time.time()
      response = requests.post(url, headers=headers, json=data, timeout=60)
      end_time = time.time()
      response_time = end_time - start_time
      model_output = response.json()['choices'][0]['message']['content']
      truncated_messages, output_tokens = num_tokens_from_messages_codellama(messages, tokenizer, 15800)
      return input_tokens, output_tokens, response.json()['choices'][0]['message']['content'], response_time
    except:
      return 'No Response Generated -- API Request Time-out (Took > 200 s to respond)'

