import os
import streamlit as st
from dotenv import load_dotenv

# LangChain & LangGraph Imports
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing import Annotated, TypedDict

load_dotenv()

st.set_page_config(page_title="Hardware-Agent AI Controller", page_icon="🚦", layout="wide")

st.title("🚦 Agentic AI Traffic Light & Verilog Controller")
st.caption("Control physical Verilog state machines using autonomous AI agents powered by LangGraph.")

# Initialize Hardware FSM State
if "fsm_state" not in st.session_state:
    st.session_state.fsm_state = 0  # 0: NS_GREEN, 1: NS_YELLOW, 2: EW_GREEN, 3: EW_YELLOW
if "fsm_timer" not in st.session_state:
    st.session_state.fsm_timer = 0
if "em_ns" not in st.session_state:
    st.session_state.em_ns = False
if "em_ew" not in st.session_state:
    st.session_state.em_ew = False
if "log_history" not in st.session_state:
    st.session_state.log_history = ["System initialized."]
if "messages" not in st.session_state:
    st.session_state.messages = []

STATE_NAMES = ["S_NS_GREEN (00)", "S_NS_YELLOW (01)", "S_EW_GREEN (10)", "S_EW_YELLOW (11)"]

# --- HARDWARE TOOL DEFINITIONS FOR AI AGENT ---
@tool
def trigger_clock_steps(steps: int = 1) -> str:
    """Steps the system clock by N cycles in the Verilog traffic light controller."""
    for _ in range(steps):
        if not st.session_state.em_ns and not st.session_state.em_ew:
            st.session_state.fsm_timer += 1
            if (st.session_state.fsm_state in [0, 2]) and st.session_state.fsm_timer >= 10:
                st.session_state.fsm_state = (st.session_state.fsm_state + 1) % 4
                st.session_state.fsm_timer = 0
            elif (st.session_state.fsm_state in [1, 3]) and st.session_state.fsm_timer >= 3:
                st.session_state.fsm_state = (st.session_state.fsm_state + 1) % 4
                st.session_state.fsm_timer = 0
    
    current_state = STATE_NAMES[st.session_state.fsm_state]
    msg = f"Clock advanced by {steps} steps. Current state: {current_state}, Timer: {st.session_state.fsm_timer}."
    st.session_state.log_history.append(msg)
    return msg

@tool
def trigger_emergency_override(direction: str) -> str:
    """Triggers or clears emergency override. Input direction should be 'NS', 'EW', or 'CLEAR'."""
    dir_upper = direction.upper()
    if dir_upper == "NS":
        st.session_state.em_ns = True
        st.session_state.em_ew = False
        msg = "🚨 EMERGENCY OVERRIDE ACTIVATED: North-South path set to GREEN."
    elif dir_upper == "EW":
        st.session_state.em_ew = True
        st.session_state.em_ns = False
        msg = "🚨 EMERGENCY OVERRIDE ACTIVATED: East-West path set to GREEN."
    else:
        st.session_state.em_ns = False
        st.session_state.em_ew = False
        msg = "✅ Emergency override cleared. Resuming normal FSM cycling."
    
    st.session_state.fsm_timer = 0
    st.session_state.log_history.append(msg)
    return msg

@tool
def get_hardware_status() -> str:
    """Returns the current state, timer, and signal outputs of the Verilog Traffic Light Controller."""
    status = (
        f"FSM State: {STATE_NAMES[st.session_state.fsm_state]} | "
        f"Timer: {st.session_state.fsm_timer}/10 | "
        f"Emergency NS: {st.session_state.em_ns} | "
        f"Emergency EW: {st.session_state.em_ew}"
    )
    return status

tools = [trigger_clock_steps, trigger_emergency_override, get_hardware_status]

# --- LANGGRAPH AGENT SETUP ---
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

def build_agent_graph(llm):
    llm_with_tools = llm.bind_tools(tools)

    def agent_node(state: AgentState):
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    def tool_node(state: AgentState):
        last_message = state["messages"][-1]
        tool_outputs = []
        for tool_call in last_message.tool_calls:
            t_name = tool_call["name"]
            t_args = tool_call["args"]
            
            if t_name == "trigger_clock_steps":
                res = trigger_clock_steps.invoke(t_args)
            elif t_name == "trigger_emergency_override":
                res = trigger_emergency_override.invoke(t_args)
            elif t_name == "get_hardware_status":
                res = get_hardware_status.invoke(t_args)
            else:
                res = "Unknown tool."
            
            tool_outputs.append(ToolMessage(content=str(res), tool_call_id=tool_call["id"]))
        return {"messages": tool_outputs}

    def should_continue(state: AgentState):
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    workflow.add_edge("tools", "agent")

    return workflow.compile()

# --- SIDEBAR & UI LAYOUT ---
with st.sidebar:
    st.header("⚙️ Agent Settings")
    api_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key

col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("🤖 AI Command Center")
    for msg in st.session_state.messages:
        if isinstance(msg, HumanMessage):
            st.chat_message("user").write(msg.content)
        elif isinstance(msg, AIMessage) and msg.content:
            st.chat_message("assistant").write(msg.content)

    user_input = st.chat_input("e.g. 'An emergency vehicle is approaching from North-South. Override the light!'")

    if user_input:
        if not os.getenv("OPENAI_API_KEY"):
            st.error("Please provide an OpenAI API Key in the sidebar.")
            st.stop()

        st.session_state.messages.append(HumanMessage(content=user_input))
        st.chat_message("user").write(user_input)

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
        graph = build_agent_graph(llm)

        with st.chat_message("assistant"):
            status_container = st.status("🧠 Agent Evaluating Hardware Command...", expanded=True)
            inputs = {"messages": st.session_state.messages}
            final_res = ""

            for event in graph.stream(inputs, stream_mode="values"):
                latest_msg = event["messages"][-1]
                if hasattr(latest_msg, "tool_calls") and latest_msg.tool_calls:
                    for tc in latest_msg.tool_calls:
                        status_container.write(f"🔧 **Executing Hardware Action:** `{tc['name']}` ({tc['args']})")
                elif isinstance(latest_msg, ToolMessage):
                    status_container.write(f"📥 **Hardware Response:** `{latest_msg.content}`")
                elif isinstance(latest_msg, AIMessage) and latest_msg.content:
                    final_res = latest_msg.content

            status_container.update(label="✅ Hardware State Updated", state="complete", expanded=False)
            st.write(final_res)
            st.session_state.messages.append(AIMessage(content=final_res))
            st.rerun()

with col2:
    st.subheader("🚦 Verilog Hardware State Monitor")
    
    # Render Current Light Signals
    if st.session_state.em_ns:
        ns_light, ew_light = "🟢 GREEN", "🔴 RED"
    elif st.session_state.em_ew:
        ns_light, ew_light = "🔴 RED", "🟢 GREEN"
    else:
        st_idx = st.session_state.fsm_state
        ns_light = "🟢 GREEN" if st_idx == 0 else ("🟡 YELLOW" if st_idx == 1 else "🔴 RED")
        ew_light = "🟢 GREEN" if st_idx == 2 else ("🟡 YELLOW" if st_idx == 3 else "🔴 RED")

    st.metric("North-South Light Output (`light_ns`)", ns_light)
    st.metric("East-West Light Output (`light_ew`)", ew_light)
    st.metric("FSM Current State (`state`)", STATE_NAMES[st.session_state.fsm_state])
    st.metric("Internal Timer Counter (`timer`)", f"{st.session_state.fsm_timer} cycles")

    st.subheader("📋 Hardware Execution Log")
    for log in reversed(st.session_state.log_history[-8:]):
        st.write(f"- {log}")
