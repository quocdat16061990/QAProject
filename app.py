"""
Streamlit Video Generator - Tạo video từ prompt qua n8n
Nhập prompt → Gọi n8n → Sinh video → Hiển thị
"""

import streamlit as st
import requests
import os
from pathlib import Path
import time
import json

# ============================================
# CẤU HÌNH N8N - THAY ĐỔI Ở ĐÂY
# ============================================
N8N_WEBHOOK_URL = "https://your-n8n-url.com/webhook/generate-video"
# ============================================

# Cấu hình trang
st.set_page_config(
    page_title="AI Video Generator",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tạo thư mục lưu video
VIDEO_DIR = Path("generated_videos")
VIDEO_DIR.mkdir(exist_ok=True)

# CSS tùy chỉnh
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 40px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 3em;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .main-header p {
        color: rgba(255,255,255,0.9);
        margin-top: 10px;
        font-size: 1.2em;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 15px;
        font-weight: bold;
        font-size: 18px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    .prompt-box {
        padding: 25px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        margin: 20px 0;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .video-card {
        padding: 25px;
        background: white;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-top: 4px solid #667eea;
    }
    .success-box {
        padding: 20px;
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-radius: 12px;
        border-left: 5px solid #28a745;
        margin: 20px 0;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .info-section {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
    }
    </style>
""", unsafe_allow_html=True)

def call_n8n_webhook(prompt: str, n8n_url: str, additional_params: dict = None) -> dict:
    """Gọi webhook n8n để tạo video"""
    try:
        # Chuẩn bị payload
        payload = {
            "prompt": prompt,
            "timestamp": int(time.time())
        }
        
        # Thêm các tham số bổ sung nếu có
        if additional_params:
            payload.update(additional_params)
        
        # Gọi n8n webhook
        response = requests.post(
            n8n_url,
            json=payload,
            timeout=300  # Timeout 5 phút
        )
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        return {
            "success": True,
            "data": result
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Timeout: n8n mất quá nhiều thời gian để xử lý"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def download_video_from_url(url: str, filename: str = None) -> str:
    """Tải video từ URL về local"""
    try:
        if not filename:
            filename = f"video_{int(time.time())}.mp4"
        
        filepath = VIDEO_DIR / filename
        
        # Tải video
        response = requests.get(url, stream=True, timeout=120)
        response.raise_for_status()
        
        # Lưu file
        total_size = int(response.headers.get('content-length', 0))
        with open(filepath, 'wb') as f:
            if total_size > 0:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
            else:
                f.write(response.content)
        
        return str(filepath)
    except Exception as e:
        st.error(f"❌ Lỗi khi tải video: {str(e)}")
        return None

def get_video_size(filepath: str) -> str:
    """Lấy kích thước file"""
    try:
        size_bytes = os.path.getsize(filepath)
        size_mb = size_bytes / (1024 * 1024)
        return f"{size_mb:.2f} MB"
    except:
        return "N/A"

def main():
    # Header
    st.markdown("""
        <div class="main-header">
            <h1>🎥 AI Video Generator</h1>
            <p>Tạo video từ prompt với AI - Powered by n8n</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Hướng Dẫn")
        st.markdown("""
        <div class="prompt-box">
        <b>Cách sử dụng:</b><br><br>
        1️⃣ Nhập prompt mô tả video<br>
        2️⃣ Nhấn "Tạo Video"<br>
        3️⃣ Đợi AI xử lý<br>
        4️⃣ Xem và tải video<br>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Các tham số tùy chỉnh (tùy chọn)
        with st.expander("🎨 Tùy Chỉnh Video"):
            video_duration = st.slider("Độ dài (giây)", 5, 60, 10)
            video_quality = st.selectbox("Chất lượng", ["HD", "Full HD", "4K"])
            video_style = st.selectbox("Style", ["Realistic", "Animated", "Cinematic"])
            
            st.session_state.video_params = {
                "duration": video_duration,
                "quality": video_quality,
                "style": video_style
            }
        
        st.markdown("---")
        
        # Thống kê
        st.header("📊 Thống Kê")
        saved_videos = list(VIDEO_DIR.glob("*.mp4"))
        st.metric("Video đã tạo", len(saved_videos))
        
        if saved_videos and st.button("🗑️ Xóa tất cả video"):
            for video in saved_videos:
                video.unlink()
            st.rerun()
    
    # Main content
    tab1, tab2 = st.tabs(["✨ Tạo Video Mới", "📁 Video Đã Tạo"])
    
    # Tab 1: Tạo video mới
    with tab1:
        st.markdown("""
            <div class="prompt-box">
                <h3>💭 Nhập Prompt Của Bạn</h3>
                <p>Mô tả video bạn muốn tạo một cách chi tiết...</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Prompt input
        prompt = st.text_area(
            "Prompt",
            placeholder="Ví dụ: Một con mèo đang nhảy múa trong vườn hoa, ánh nắng chiều đẹp, phong cách anime...",
            height=150,
            label_visibility="collapsed"
        )
        
        # Ví dụ prompt
        with st.expander("💡 Ví Dụ Prompt Hay"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                **Phong cảnh:**
                - Bầu trời đầy sao, núi tuyết phủ trắng
                - Biển cả lúc hoàng hôn, sóng vỗ bờ
                - Thành phố về đêm, đèn neon rực rỡ
                """)
            with col2:
                st.markdown("""
                **Động vật:**
                - Con chó chạy qua cánh đồng hoa
                - Đàn chim bay trên bầu trời xanh
                - Cá bơi trong hồ nước trong veo
                """)
        
        # Generate button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            generate_button = st.button(
                "🚀 TẠO VIDEO NGAY!",
                type="primary",
                use_container_width=True
            )
        
        # Xử lý tạo video
        if generate_button:
            if not prompt.strip():
                st.error("⚠️ Vui lòng nhập prompt!")
            else:
                # Hiển thị thông tin đang xử lý
                st.markdown("""
                    <div class="info-section">
                        <h4>⏳ Đang xử lý...</h4>
                    </div>
                """, unsafe_allow_html=True)
                
                with st.spinner("🎬 Đang gửi prompt đến AI..."):
                    # Lấy tham số tùy chỉnh
                    params = st.session_state.get("video_params", {})
                    
                    # Gọi n8n với URL từ constant
                    result = call_n8n_webhook(
                        prompt, 
                        N8N_WEBHOOK_URL,
                        params
                    )
                
                if not result["success"]:
                    st.error(f"❌ Lỗi: {result['error']}")
                else:
                    st.markdown("""
                        <div class="success-box">
                            <h3 style="color: #28a745; margin: 0;">✅ Tạo video thành công!</h3>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Lấy URL video từ response
                    response_data = result["data"]
                    
                    # Hiển thị response để debug
                    with st.expander("🔍 Xem Response từ n8n"):
                        st.json(response_data)
                    
                    # Tìm URL video trong response
                    video_url = None
                    
                    # Thử các khả năng response structure
                    if isinstance(response_data, dict):
                        video_url = (
                            response_data.get("video_url") or
                            response_data.get("url") or
                            response_data.get("videoUrl") or
                            response_data.get("file_url")
                        )
                    elif isinstance(response_data, str):
                        video_url = response_data
                    
                    if video_url:
                        # Tải video về
                        with st.spinner("📥 Đang tải video về..."):
                            filename = f"prompt_{int(time.time())}.mp4"
                            video_path = download_video_from_url(video_url, filename)
                        
                        if video_path:
                            # Hiển thị thông tin
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("📁 Tên file", os.path.basename(video_path))
                            with col2:
                                st.metric("📊 Kích thước", get_video_size(video_path))
                            
                            # Hiển thị prompt đã dùng
                            st.info(f"💭 Prompt: {prompt}")
                            
                            # Hiển thị video
                            st.video(video_path)
                            
                            # Nút tải xuống
                            with open(video_path, "rb") as f:
                                st.download_button(
                                    label="📥 Tải Video Về Máy",
                                    data=f.read(),
                                    file_name=os.path.basename(video_path),
                                    mime="video/mp4",
                                    use_container_width=True
                                )
                    else:
                        st.warning("⚠️ Không tìm thấy URL video trong response. Vui lòng kiểm tra n8n workflow.")
    
    # Tab 2: Video đã tạo
    with tab2:
        st.subheader("📁 Video Đã Tạo")
        
        saved_videos = sorted(
            VIDEO_DIR.glob("*.mp4"), 
            key=os.path.getmtime, 
            reverse=True
        )
        
        if not saved_videos:
            st.info("📭 Chưa có video nào. Hãy tạo video mới ở tab 'Tạo Video Mới'!")
        else:
            for video_path in saved_videos:
                with st.container():
                    st.markdown(f"""
                        <div class="video-card">
                            <h4>🎬 {video_path.name}</h4>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.metric("📊 Kích thước", get_video_size(str(video_path)))
                        st.caption(f"Tạo lúc: {time.ctime(video_path.stat().st_mtime)}")
                    
                    with col2:
                        with open(video_path, "rb") as f:
                            st.download_button(
                                "📥 Tải về",
                                f.read(),
                                file_name=video_path.name,
                                mime="video/mp4",
                                key=f"download_{video_path.name}"
                            )
                    
                    with col3:
                        if st.button("🗑️ Xóa", key=f"delete_{video_path.name}"):
                            video_path.unlink()
                            st.rerun()
                    
                    # Hiển thị video
                    st.video(str(video_path))
                    
                    st.markdown("---")

if __name__ == "__main__":
    main()