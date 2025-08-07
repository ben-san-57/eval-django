from langchain_ollama import ChatOllama
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate as PromptTemplate
from todolist.models import Task
from django.contrib.auth.models import User
from typing import Optional
from langgraph.graph import StateGraph, END


llm = ChatOllama(model = "llama3.1")

class AssistantState(BaseModel):
    message: Optional[str] = None
    is_task: Optional[bool] = False
    task_content: Optional[str] = None
    user_id: int
    reply: Optional[str] = None


class IsTodo(BaseModel):
    is_task: bool

detect_prompt = PromptTemplate.from_template("""Tu es un assistant intelligent qui determine si l'input de
                                      l'utilisateur est une tache a ajouter a la todo list ou pas.
                                      Tu dois répondre avec un booléen `is_task`:
                                      - `true` si l'input est une tâche à créer
                                      - `false` sinon

                                      Input de l'uyilisateur:
                                      {message}
                                      """)

def detect_task_intent(state: AssistantState) -> AssistantState:
    message = state.message
    structured_llm = llm.with_structured_output(IsTodo)
    chain = detect_prompt | structured_llm
    result = chain.invoke({"message": message})
    
    state.is_task = result.is_task
    return state

    # return AssistantState(
    #     reply=result.reply,
    #     is_task=result.is_task,
    #     user_id=state.user_id,
    #     message=state.message,
    # )

class ExtractedTask(BaseModel):
    task_content: str

extract_prompt = PromptTemplate.from_template("""
    Tu es un assistant intelligent qui extrait 
    le contenu de la tache à créer de l'input de l'utilisateur.
    Tu dois répondre avec un champs unique `task_content`.
                                                  
    Exemples :
    -"il faut que je réserve mon billet d'avion --> "Réserver mon billet d'avion"
    -"je dois faire les courses --> "Faire les courses"
    -"N'oublie pas d'acheter du pain --> "Acheter du pain"
    -"Ajoute à la todolist de préparer une éval bien compliquée!" --> "Préparer une éval bien compliquée"
                                                  
    Input de l'utilisateur:
    {message}
    """)

def extract_task_content(state: AssistantState) -> AssistantState:
    message = state.message
    structured_llm = llm.with_structured_output(ExtractedTask)
    chain = extract_prompt | structured_llm
    result = chain.invoke({"message": message})

    state.task_content = result.task_content
    return state
    
def create_task(state: AssistantState) -> AssistantState:
    task_content = state.task_content
    user_id = state.user_id

    user = User.objects.get(id=user_id)
    task = Task(
        title=task_content,
        user_id=user_id,
    )
    task.save()

    return state
    
class ReplyContent(BaseModel):
    reply: str
    
acknowledge_prompt = PromptTemplate.from_template(
    """
    Tu dois répondre à l'utilisateur pour lui indiquer que la tâche a été ajoutée à la todo list.
    Tu dois répondre de façon sympatique et amicale
        
    Tâche ajoutée à la TODO:
        {task_content}
        Message original de l'utilisateur:
        {message}
        """)

def acknowledge_task_created(state: AssistantState) -> AssistantState:
    task_content = state.task_content
    message = state.message
    structured_llm = llm.with_structured_output(ReplyContent)
    chain = acknowledge_prompt | structured_llm
    result = chain.invoke({"task_content": task_content, "message": message})
    
    # return AssistantState(
    #     reply=result.reply,
    #     is_task=state.is_task,
    #     user_id=state.user_id,
    #     message=state.message,
    # )
    state.reply = result.reply
    return state

response_prompt = PromptTemplate.from_template(
    """
    Tu dois répondre à l'utilisateur en t'appyant de tes connaissance général.
    sans rien inventer de maniere sensuelle et aguicheuse

    Question : {message}
    """
)

def respond_to_user(state: AssistantState) -> AssistantState:
    message = state.message
    structured_llm = llm.with_structured_output(ReplyContent)
    chain = response_prompt | structured_llm
    result = chain.invoke({"message": message})
    
    state.reply = result.reply
    return state
    # return AssistantState(
    #     reply=result.reply,
    #     is_task=state.is_task,
    #     user_id=state.user_id,
    #     message=state.message,
    # )

graph = StateGraph(AssistantState) 

graph.add_node("detect_task",detect_task_intent)
graph.add_node("extract_task", extract_task_content)
graph.add_node("create_task", create_task)
graph.add_node("acknowledge_task", acknowledge_task_created)
graph.add_node("respond_to_user", respond_to_user)

graph.set_entry_point("detect_task")
graph.add_conditional_edges(
    "detect_task",
    lambda state: "extract_task" if state.is_task else "respond_to_user",
)

graph.add_edge("extract_task", "create_task")
graph.add_edge("create_task", "acknowledge_task")
graph.add_edge("acknowledge_task", END)
graph.add_edge("respond_to_user", END)

assistant_graph = graph.compile()

assistant_graph.get_graph().draw_mermaid_png(output_file_path="assistant_graph.png")
