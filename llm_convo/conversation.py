from llm_convo.agents import ChatAgent


def run_conversation(agent_a: ChatAgent, agent_b: ChatAgent):
    transcript = []
    while True:
        text_a = agent_a.get_response(transcript)
        transcript.append(text_a)
        print("->", text_a, transcript)
        text_b = agent_b.get_response(transcript)
        transcript.append(text_b)
        print("->", text_b, transcript)
