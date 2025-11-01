import streamlit as st
from openai import OpenAI
from datetime import datetime

# =============================
# 1️⃣ Cấu hình & UI Setup
# (Giữ nguyên phần này)
# =============================
st.set_page_config(page_title="LLM Tool - Ollama (Local)", layout="centered")
st.markdown(
    """
    <style>
    .block-container { max-width: 1000px !important; padding-top: 2rem; }
    textarea { font-family: Consolas, monospace !important; background-color: #f8f9fa; border-radius: 8px; }
    h1, h2, h3 { color: #28a745; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px; margin-top: 20px; }
    .stButton>button { width: 100%; height: 50px; font-weight: bold; background-color: #28a745; color: white; border: none; border-radius: 10px; transition: background-color 0.3s ease, transform 0.1s; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
    .stButton>button:hover { background-color: #1e7e34; transform: translateY(-2px); }
    div[role="radiogroup"] { padding: 10px; border: 1px solid #ced4da; border-radius: 8px; background-color: #f8f9fa; margin-bottom: 20px; }
    .streamlit-expanderHeader { background-color: #e9ecef; border-radius: 8px; padding: 10px; margin-top: 5px; font-weight: 500; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🐳 LLM Tool - Ollama (Local)")
st.write("Ứng dụng sử dụng **Ollama API cục bộ**")

# =============================
# 2️⃣ Ollama Client (Thay thế OpenAI)
# =============================
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama_key_placeholder"
)

# Mô hình cục bộ
OLLAMA_MODEL = "gemma3:270m"
# =============================
# 3️⃣ Lưu lịch sử
# =============================
if "history" not in st.session_state:
    st.session_state.history = []

# =============================
# 4️⃣ Giao diện người dùng
# =============================
st.subheader("⚙️ Cấu hình mô hình")
model_names = [OLLAMA_MODEL]
default_index = 0
model = st.selectbox("Mô hình đang chạy trên Ollama", model_names, index=default_index, disabled=True)

st.warning(
    f"**Lưu ý:** Ứng dụng đang chạy mô hình **{OLLAMA_MODEL}** cục bộ. Vui lòng đảm bảo Ollama đang chạy và kiên nhẫn chờ đợi do hạn chế về tài nguyên.")

col1, col2 = st.columns([3, 1])
with col2:
    st.text("")
    st.text("")
    clear = st.button("🗑️ Xóa lịch sử")
if clear:
    st.session_state.history = []
    st.rerun()

st.subheader("📝 Nhập dữ liệu")

# --- ĐIỀU CHỈNH TASK_PROMPTS TẠI ĐÂY ---
TASK_PROMPTS = {
    # Thêm ràng buộc "chỉ trả về..." và vai trò chuyên gia
    "Tóm tắt": "Bạn là chuyên gia tóm tắt. Tóm tắt nội dung sau bằng tiếng Việt, tập trung vào các ý chính và rút gọn thành 1-2 câu. Chỉ trả về nội dung tóm tắt:",

    # Yêu cầu ngôn ngữ cụ thể và không giải thích
    "Dịch sang tiếng Pháp": "Bạn là chuyên gia dịch thuật tiếng Pháp. Dịch câu sau sang tiếng Pháp chuẩn, chỉ trả về nội dung dịch (không kèm theo bất kỳ giải thích, chào hỏi, hay tiêu đề nào khác):",

    # Giữ vai trò thân thiện, yêu cầu dùng từ ngữ đơn giản
    "Giải thích đơn giản": "Bạn là một giáo viên thân thiện. Giải thích nội dung sau bằng ngôn ngữ cực kỳ đơn giản, dễ hiểu, chỉ dùng từ ngữ dành cho học sinh lớp 5:",

    # Ràng buộc format output cụ thể
    "Trích xuất từ khóa": "Trích xuất 5 từ khóa hoặc cụm từ quan trọng nhất từ văn bản sau. Mỗi từ khóa phải nằm trên một dòng riêng biệt, không đánh số thứ tự và không có ký tự đặc biệt nào khác:",

    # Yêu cầu cú pháp code và giải thích ngắn gọn
    "Tạo mã Python": "Bạn là một lập trình viên Python chuyên nghiệp. Viết mã Python để thực hiện yêu cầu sau, kèm theo giải thích ngắn gọn. Đặt mã Python trong khối Markdown ````python ... ````:",
}
# --- KẾT THÚC ĐIỀU CHỈNH ---

task = st.radio("Chọn tác vụ", list(TASK_PROMPTS.keys()), horizontal=True)
text = st.text_area("Nội dung đầu vào", height=180, placeholder="Nhập đoạn văn hoặc yêu cầu...", key="input_text")
st.divider()


# =============================
# 5️⃣ Hàm gọi Ollama API
# (Giữ nguyên phần này)
# =============================
def get_ollama_response(model, prompt, output_placeholder, task):
    full_response = ""
    st.info(f"Đang xử lý bằng mô hình: **{model}** trên Ollama...")
    error_msg = None

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        full_response = response.choices[0].message.content

        if task == "Tạo mã Python":
            output_placeholder.code(full_response, language="python")
        else:
            output_placeholder.markdown(full_response)

        st.success("✅ Hoàn tất.")

    except Exception as e:
        if "Connection" in str(e) or "Failed to establish a new connection" in str(e):
            error_msg = f"❌ Lỗi kết nối: Ollama có đang chạy không? Vui lòng kiểm tra dịch vụ!"
        else:
            error_msg = f"❌ Đã xảy ra lỗi: {e}"
        st.error(error_msg)

    return full_response, error_msg


# =============================
# 6️⃣, 7️⃣, 8️⃣ Phần còn lại của code (Giữ nguyên)
# =============================
def save_result(task, model, text, result):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"result_{task.replace(' ', '_')}_{timestamp}_Ollama.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("=== LLM TOOL RESULT (Ollama Local) ===\n")
        f.write(f"Task: {task}\n")
        f.write(f"Model: {model}\n")
        f.write(f"Time: {timestamp}\n\n")
        f.write("----- Input -----\n")
        f.write(text.strip() + "\n\n")
        f.write("----- Output -----\n")
        f.write(result.strip() + "\n")
    return filename


if st.button("Chạy tác vụ"):
    if not text.strip():
        st.warning("Vui lòng nhập nội dung trước khi xử lý.")
    else:
        current_model = OLLAMA_MODEL
        prompt = f"{TASK_PROMPTS[task]}\n\n{text}"
        st.subheader("📝 Kết quả")
        output_box = st.empty()

        result, error_msg = get_ollama_response(current_model, prompt, output_box, task)

        if not error_msg:
            entry = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "task": task,
                "model": current_model,
                "text": text,
                "result": result
            }
            st.session_state.history.insert(0, entry)

            filename = save_result(task, current_model, text, result)
            try:
                with open(filename, "r", encoding="utf-8") as file:
                    st.download_button(
                        label="⬇️ Tải kết quả (.txt)",
                        data=file.read(),
                        file_name=filename,
                        mime="text/plain",
                        use_container_width=True
                    )
            except Exception:
                st.warning("Không thể tạo file tải xuống.")

if st.session_state.history:
    st.divider()
    st.subheader("📚 Lịch sử hội thoại")
    for i, item in enumerate(st.session_state.history):
        with st.expander(f"{item['time']} – {item['task']} ({item['model']})"):
            st.markdown(f"**Tác vụ:** {item['task']}")
            st.markdown(f"**Mô hình:** {item['model']}")
            st.markdown("**Đầu vào:**")
            st.code(item["text"], language="text")
            st.markdown("**Kết quả:**")
            if item["task"] == "Tạo mã Python":
                st.code(item["result"], language="python")
            else:
                st.write(item["result"])
