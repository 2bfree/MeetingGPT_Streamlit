import openai
import time
import tiktoken


def num_tokens_from_messages_gpt35_turbo(messages, max_length, model="gpt-3.5-turbo-16k"):
  """Returns the number of tokens used by a list of messages."""
  try:
      encoding = tiktoken.encoding_for_model(model)
  except KeyError:
      encoding = tiktoken.get_encoding("cl100k_base")
  if model == "gpt-3.5-turbo-16k":  # note: future models may deviate from this
      num_tokens = 0
      truncated_messages = []
      for message in messages:
          num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
          truncated_message = message.copy()
          for key, value in message.items():
              tokenized_message = encoding.encode(value)
              token_length = len(tokenized_message)
              if num_tokens + token_length > max_length:
                  # Truncate the value to fit within the token limit
                  remaining_tokens = max_length - num_tokens
                  truncated_value = encoding.decode(tokenized_message[:remaining_tokens])
                  truncated_message[key] = truncated_value
                  truncated_message["role"] = message.get("role", "user")
                  truncated_messages.append(truncated_message)
                  return truncated_messages, max_length
          for key, value in message.items():
              num_tokens += len(encoding.encode(value))
              if key == "name":  # if there's a name, the role is omitted
                  num_tokens += -1  # role is always required and always 1 token
      num_tokens += 2  # every reply is primed with <im_start>assistant
      return [], num_tokens
  else:
      raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
  See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")

def gpt35_meeting_analytics(transcription):

    input_query=[
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
        ]

    truncated_messages, input_tokens = num_tokens_from_messages_gpt35_turbo(input_query, 14838)

    if len(truncated_messages) > 0:
      input_query=[
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
            {"role": "user", "content": "Here is the meeting transcript: " +  str(truncated_messages[0]['content'])}
        ]

    if input_tokens <= 14838:
      start_time = time.time()
      response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        temperature=0,
        messages=input_query,
        timeout=1000,
        max_tokens=1500
      )
      end_time = time.time()
      response_time = end_time - start_time
      model_output = response['choices'][0]['message']['content']
      messages = [{"role": "system", "content": model_output}]
      truncated_messages, output_tokens = num_tokens_from_messages_gpt35_turbo(messages, 14838)
      return input_tokens, output_tokens, response['choices'][0]['message']['content'], response_time

    else:
      return input_tokens, 0, 'No Response Generated -- # of Input Tokens Exceeds 16000', 0
    
def reformat_gpt35(answer):
    input_query=[{ "role": "system",
                "content": "As an AI with expertise in taking your answers and re-formatting them into a specified format, \
                your task is to take the answer I provide below and return it in the format resembling this Sample Answer: \
                \
                Sample Answer Format (Not the same meeting, but to demonstrate desired format): \
                \
                ```Prompt #1 Answer - Abstract Summary \
                The team discussed progress on the application building and containerization. They reviewed the \
                current state of the application and discussed design choices for the user interface. They also \
                talked about integrating the Lama 2 model and generating data from the AMI corpus. The team \
                discussed the need for user-defined metadata and the possibility of storing previous meeting \
                outputs. They also discussed the deployment process and the use of AWS. The team agreed to continue \
                working on their respective tasks and to meet again to set up AWS and finalize the application \
                design. \
                \
                Prompt #2 Answer - Topics & Engagement \
                1. Application building and containerizing (20%) \
                2. Integration of different components (15%) \
                3. Use of different language models (10%) \
                4. User interface design and functionality (15%) \
                5. User data storage and privacy considerations (10%) \
                6. Stakeholder engagement metrics and visualizations (10%) \
                7. AWS services and code integration (10%) \
                8. Elevator pitch preparation (10%) \
                \
                Participant Contributions: \
                Chase Iver Madson: 40% speaking time, 5 interactions \
                Siva Chamiraju: 20% speaking time, 3 interactions \
                Michael Townsend: 25% speaking time, 4 interactions \
                Francis J Lee: 15% speaking time, 3 interactions \
                \
                Prompt #3 Answer - Action Items \
                - Chase Iver Madson: (3 Actions) \
	                  - Create a shared S3 bucket for storing the dataset and model \
	                  - Set up a cloud-based platform for hosting the model and dataset \
	                  - Develop a simple version of the application to connect the API with the user interface \
                - Siva Chamiraju: (3 Actions) \
	                  - Set up an AWS organization to share credits and resources \
	                  - Create an S3 bucket for storing the dataset and model \
	                  - Help with setting up the cloud-based platform \
                - Francis J Lee: (2 Actions) \
	                  - Help with setting up the cloud-based platform \
	                  - Develop a simple version of the application to connect the API with the user interface \
                - Michael Townsend: (2 Actions) \
	                  - Fine-tune a pre-trained language model on a dataset of meeting transcripts \
	                  - Develop a simple version of the application to connect the API with the user interface \
                \
                Prompt #4 Answer - Sentiment \
                Collaborative``` \
                \
                Be sure to pay special attention to ensuring the percentages and numbers are included in the reformatted \
                answer in the same way as the example."
            },
            {
                "role": "user",
                "content": "Answer you will be reformtting to the format provided:" + answer
            }
        ]

    truncated_messages, input_tokens = num_tokens_from_messages_gpt35_turbo(input_query, 16000)

    start_time = time.time()
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo-16k",
      temperature=0,
      messages=input_query,
      timeout=200
    )
    end_time = time.time()
    response_time = end_time - start_time
    model_output = response['choices'][0]['message']['content']
    messages = [{"role": "system", "content": model_output}]
    truncated_messages, output_tokens = num_tokens_from_messages_gpt35_turbo(messages, 16000)
    return input_tokens, output_tokens, response['choices'][0]['message']['content'], response_time


def qa_extraction_gpt35(question, transcription):
    input_query=[
            {"role": "system", "content": "You are a highly skilled AI trained in language comprehension and summarization. \
            I would like you to read the meeting transcript provided and use the information contained in it to answer questions. \
            Please make sure that your responses: \
            1. Provide answers to the users questions clearly and concisely \
            2. Avoid repeating the same points multiple times. \
            3. Use a variety of formats and descriptions to present the key points. \
            Feel free to use bullet points, paraphrases, and varying levels of detail to summarize the essential content comprehensively."},
            {"role": "user", "content": transcription}
        ]
    truncated_messages, input_tokens = num_tokens_from_messages_gpt35_turbo(input_query, 15800)

    if len(truncated_messages) > 0:
        input_query=[
            {"role": "system", "content": "You are a highly skilled AI trained in language comprehension and summarization. \
            I would like you to read the meeting transcript provided and use the information contained in it to answer questions. \
            Please make sure that your responses: \
            1. Provide answers to the users questions clearly and concisely \
            2. Avoid repeating the same points multiple times. \
            3. Use a variety of formats and descriptions to present the key points. \
            Feel free to use bullet points, paraphrases, and varying levels of detail to summarize the essential content comprehensively."},
            {"role": "user", "content": truncated_messages[0]['content']},
            {"role": "user", "content": question}
        ]
    else:
        input_query=[
            {"role": "system", "content": "You are a highly skilled AI trained in language comprehension and summarization. \
            I would like you to read the meeting transcript provided and use the information contained in it to answer questions. \
            Please make sure that your responses: \
            1. Provide answers to the users questions clearly and concisely \
            2. Avoid repeating the same points multiple times. \
            3. Use a variety of formats and descriptions to present the key points. \
            Feel free to use bullet points, paraphrases, and varying levels of detail to summarize the essential content comprehensively."},
            {"role": "user", "content": transcription},
            {"role": "user", "content": question}
        ]

    if input_tokens <= 15800:
      start_time = time.time()
      response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        temperature=0,
        messages=input_query,
        timeout=60
      )
      end_time = time.time()
      response_time = end_time - start_time
      model_output = response['choices'][0]['message']['content']
      messages = [{"role": "system", "content": model_output}]
      truncated_messages, output_tokens = num_tokens_from_messages_gpt35_turbo(messages, 15800)
      return input_tokens, output_tokens, response['choices'][0]['message']['content'], response_time
    else:
      return input_tokens, 0, 'No Response Generated -- # of Input Tokens Exceeds 16000', 0