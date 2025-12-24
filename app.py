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
import threading

# ============================================
# CẤU HÌNH N8N - THAY ĐỔI Ở ĐÂY
# ============================================
N8N_WEBHOOK_URL = st.secrets.get("WEBHOOK_URL")
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
        background: linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%);
        border-radius: 15px;
        margin: 20px 0;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        color: white;
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
    .progress-container {
        background: white;
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 5px solid #667eea;
    }
    .progress-text {
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        color: #667eea;
        margin-top: 10px;
    }
    .stVideo {
        max-width: 100% !important;
        margin: 0 auto;
    }
    video {
        width: 100% !important;
        max-height: 600px !important;
        object-fit: contain !important;
    }
    </style>
""", unsafe_allow_html=True)

def call_n8n_webhook(prompt: str, n8n_url: str, additional_params: dict = None) -> dict:
    """Gọi webhook n8n để tạo video"""
    print("\n" + "="*80)
    print("🚀 BẮT ĐẦU GỌI N8N WEBHOOK")
    print("="*80)
    print(f"📝 Prompt: {prompt}")
    print(f"🔗 URL: {n8n_url}")
    print(f"⏰ Timestamp: {int(time.time())}")
    
    start_time = time.time()  # Định nghĩa trước để dùng trong exception handler
    try:
        # Chuẩn bị payload
        payload = {
            "prompt": prompt,
            "timestamp": int(time.time())
        }
        
        # Thêm các tham số bổ sung nếu có
        if additional_params:
            payload.update(additional_params)
            print(f"📦 Additional params: {json.dumps(additional_params, indent=2, ensure_ascii=False)}")
        
        print(f"\n📤 PAYLOAD GỬI ĐI:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        
        # Gọi n8n webhook với timeout dài hơn (15 phút)
        print(f"\n⏳ Đang gửi request đến n8n...")
        print(f"⏱️ Timeout: 15 phút (900 giây)")
        start_time = time.time()
        response = requests.post(
            n8n_url,
            json=payload,
            timeout=2900  # Timeout 15 phút (900 giây) để xử lý video dài
        )
        elapsed_time = time.time() - start_time
        elapsed_minutes = int(elapsed_time // 60)
        elapsed_seconds = int(elapsed_time % 60)
        print(f"✅ Nhận được response sau {elapsed_minutes} phút {elapsed_seconds} giây ({elapsed_time:.2f} giây)")
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        response.raise_for_status()
        
        # Kiểm tra response content trước khi parse
        response_text = response.text
        print(f"\n📥 Response text (first 500 chars): {response_text[:500]}")
        print(f"📏 Response text length: {len(response_text)}")
        
        # Kiểm tra nếu response rỗng
        if not response_text or not response_text.strip():
            print(f"\n❌ ERROR: Response rỗng!")
            print("="*80 + "\n")
            return {
                "success": False,
                "error": "Response từ server rỗng. Vui lòng kiểm tra n8n workflow."
            }
        
        # Parse response JSON
        print(f"\n📥 Đang parse response JSON...")
        try:
            result = response.json()
            print(f"✅ Parse thành công!")
            print(f"\n📦 RESPONSE DATA:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("="*80 + "\n")
            
            return {
                "success": True,
                "data": result
            }
        except json.JSONDecodeError as json_err:
            print(f"\n❌ JSON DECODE ERROR: {str(json_err)}")
            print(f"📄 Response text: {response_text[:1000]}")
            print("="*80 + "\n")
            return {
                "success": False,
                "error": f"Response không phải JSON hợp lệ. Response: {response_text[:200]}"
            }
    except requests.exceptions.Timeout:
        elapsed_time = time.time() - start_time
        elapsed_minutes = int(elapsed_time // 60)
        elapsed_seconds = int(elapsed_time % 60)
        print(f"\n❌ TIMEOUT ERROR sau {elapsed_minutes} phút {elapsed_seconds} giây")
        print(f"⏱️ Timeout limit: 15 phút (900 giây)")
        print("="*80 + "\n")
        return {
            "success": False,
            "error": f"Timeout: Quá trình xử lý mất hơn 15 phút ({elapsed_minutes} phút {elapsed_seconds} giây). Vui lòng thử lại với prompt ngắn hơn hoặc liên hệ hỗ trợ."
        }
    except requests.exceptions.RequestException as e:
        print(f"\n❌ REQUEST ERROR: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text[:500]}")
        print("="*80 + "\n")
        return {
            "success": False,
            "error": f"Request error: {str(e)}"
        }
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")
        print("="*80 + "\n")
        return {
            "success": False,
            "error": str(e)
        }

def download_video_from_url(url: str, filename: str = None) -> str:
    """Tải video từ URL về local"""
    print("\n" + "="*80)
    print("📥 BẮT ĐẦU TẢI VIDEO")
    print("="*80)
    print(f"🔗 URL: {url}")
    print(f"📁 Filename: {filename}")
    
    try:
        if not filename:
            filename = f"video_{int(time.time())}.mp4"
        
        filepath = VIDEO_DIR / filename
        print(f"💾 Filepath: {filepath}")
        
        # Tải video
        print(f"⏳ Đang gửi request GET...")
        start_time = time.time()
        response = requests.get(url, stream=True, timeout=120)
        elapsed = time.time() - start_time
        print(f"✅ Nhận được response sau {elapsed:.2f} giây")
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        response.raise_for_status()
        
        # Lưu file
        total_size = int(response.headers.get('content-length', 0))
        print(f"📏 Total size: {total_size} bytes ({total_size / (1024*1024):.2f} MB)" if total_size > 0 else "📏 Total size: Unknown")
        
        print(f"💾 Đang lưu file...")
        with open(filepath, 'wb') as f:
            if total_size > 0:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if downloaded % (1024 * 1024) == 0:  # Log mỗi MB
                        print(f"  ⬇️ Đã tải: {downloaded / (1024*1024):.2f} MB / {total_size / (1024*1024):.2f} MB")
            else:
                f.write(response.content)
                print(f"  ✅ Đã tải toàn bộ content")
        
        file_size = os.path.getsize(filepath)
        print(f"✅ Tải thành công!")
        print(f"📊 File size: {file_size} bytes ({file_size / (1024*1024):.2f} MB)")
        print(f"📁 File path: {filepath}")
        print("="*80 + "\n")
        
        return str(filepath)
    except Exception as e:
        print(f"\n❌ LỖI KHI TẢI VIDEO: {str(e)}")
        import traceback
        print(traceback.format_exc())
        print("="*80 + "\n")
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
                # Tạo placeholder riêng cho "Đang tạo video..." để có thể clear dễ dàng
                creating_video_placeholder = st.empty()
                creating_video_placeholder.markdown("""
                    <div class="progress-container">
                        <h3 style="text-align: center; color: #667eea; margin-bottom: 20px;">🎬 Đang tạo video...</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                # Tạo progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Lấy tham số tùy chỉnh
                params = st.session_state.get("video_params", {})
                
                # Biến để lưu kết quả API
                api_result = {"result": None, "done": False, "error": None}
                
                def call_api():
                    """Gọi API trong thread riêng"""
                    print("\n" + "="*80)
                    print("🔄 THREAD: Bắt đầu gọi API")
                    print(f"📝 Prompt: {prompt[:100]}...")
                    print(f"🔗 URL: {N8N_WEBHOOK_URL}")
                    print(f"📦 Params: {params}")
                    print("="*80)
                    try:
                        result = call_n8n_webhook(
                            prompt, 
                            N8N_WEBHOOK_URL,
                            params
                        )
                        print(f"\n✅ THREAD: API call thành công")
                        print(f"📊 Result success: {result.get('success')}")
                        api_result["result"] = result
                    except Exception as e:
                        print(f"\n❌ THREAD: Exception trong call_api: {str(e)}")
                        import traceback
                        print(traceback.format_exc())
                        api_result["error"] = str(e)
                        api_result["result"] = {"success": False, "error": str(e)}
                    finally:
                        api_result["done"] = True
                        print(f"🏁 THREAD: Hoàn thành, done = True\n")
                
                # Bắt đầu gọi API trong thread riêng
                api_thread = threading.Thread(target=call_api, daemon=True)
                api_thread.start()
                
                # Progress steps với thông điệp
                progress_steps = [
                    (5, "📝 Đang gửi prompt đến server..."),
                    (15, "🔍 Đang phân loại prompt..."),
                    (30, "🤖 Đang tạo kịch bản video với AI..."),
                    (50, "📊 Đang xử lý dữ liệu..."),
                    (70, "🎬 Đang tạo kịch bản chi tiết..."),
                    (85, "⏳ Đang hoàn thiện kịch bản..."),
                    (95, "✨ Đang xử lý cuối cùng..."),
                ]
                
                # Update progress bar trong khi đợi API
                current_progress = 0
                step_index = 0
                start_time = time.time()
                
                while not api_result["done"]:
                    # Tính progress dựa trên thời gian (tối đa 95%)
                    elapsed = time.time() - start_time
                    time_based_progress = min(95, int(elapsed * 2))  # Tăng 2% mỗi giây
                    
                    # Update progress với các bước đã định nghĩa
                    if step_index < len(progress_steps):
                        step_progress, step_message = progress_steps[step_index]
                        if time_based_progress >= step_progress:
                            current_progress = step_progress
                            progress_bar.progress(current_progress / 100)
                            status_text.markdown(f"""
                                <div class="progress-text">
                                    {step_message} <span style="color: #764ba2;">{current_progress}%</span>
                                </div>
                            """, unsafe_allow_html=True)
                            step_index += 1
                    else:
                        # Nếu đã qua tất cả các bước, dùng time-based progress
                        if time_based_progress > current_progress:
                            current_progress = time_based_progress
                            progress_bar.progress(current_progress / 100)
                            status_text.markdown(f"""
                                <div class="progress-text">
                                    ⏳ Đang xử lý với AI... <span style="color: #764ba2;">{current_progress}%</span>
                                </div>
                            """, unsafe_allow_html=True)
                    
                    time.sleep(0.1)  # Update mỗi 0.1 giây
                
                # API đã hoàn thành
                result = api_result["result"]
                
                # Clear NGAY LẬP TỨC phần "🎬 Đang tạo video..." và progress bar
                creating_video_placeholder.empty()
                progress_bar.empty()
                status_text.empty()
                
                if not result["success"]:
                    st.error(f"❌ Lỗi: {result['error']}")
                else:
                    # Hiển thị thông báo thành công
                    st.markdown("""
                        <div class="success-box">
                            <h3 style="color: #28a745; margin: 0;">✅ Tạo kịch bản thành công!</h3>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Lấy URL video từ response
                    response_data = result["data"]
                    
                    # Log response để debug
                    print("\n" + "="*80)
                    print("📥 XỬ LÝ RESPONSE DATA")
                    print("="*80)
                    print(f"📊 Response data type: {type(response_data).__name__}")
                    print(f"📏 Response data length/size: {len(response_data) if hasattr(response_data, '__len__') else 'N/A'}")
                    print(f"\n📦 FULL RESPONSE DATA:")
                    print(json.dumps(response_data, indent=2, ensure_ascii=False))
                    print("="*80)
                    
                    # Tìm URL video trong response
                    video_url = None
                    video_name = None
                    
                    print(f"\n🔍 BẮT ĐẦU TÌM VIDEO URL...")
                    
                    # Xử lý response có thể là array (Google Drive response)
                    if isinstance(response_data, list):
                        print(f"✅ Response là LIST, có {len(response_data)} phần tử")
                        if len(response_data) > 0:
                            # Lấy phần tử đầu tiên nếu là array
                            drive_file = response_data[0]
                            print(f"📄 Phần tử đầu tiên type: {type(drive_file).__name__}")
                            if isinstance(drive_file, dict):
                                print(f"📋 Keys trong drive_file: {list(drive_file.keys())[:10]}...")
                                # Lấy URL từ Google Drive
                                video_url = (
                                    drive_file.get("webContentLink") or
                                    drive_file.get("webViewLink") or
                                    drive_file.get("downloadUrl")
                                )
                                video_name = drive_file.get("name") or drive_file.get("originalFilename")
                                print(f"🔗 webContentLink: {drive_file.get('webContentLink')}")
                                print(f"🔗 webViewLink: {drive_file.get('webViewLink')}")
                                print(f"🔗 downloadUrl: {drive_file.get('downloadUrl')}")
                                print(f"📝 name: {drive_file.get('name')}")
                                print(f"📝 originalFilename: {drive_file.get('originalFilename')}")
                                
                                # Convert Google Drive view link to direct download
                                if video_url and "drive.google.com/file/d/" in video_url:
                                    file_id = video_url.split("/file/d/")[1].split("/")[0]
                                    print(f"🆔 Extracted file_id: {file_id}")
                                    video_url = f"https://drive.google.com/uc?export=download&id={file_id}"
                                    print(f"✅ Converted to direct download: {video_url}")
                                elif video_url and "uc?id=" in video_url:
                                    print(f"✅ Đã là direct download link")
                        else:
                            print("⚠️ List rỗng!")
                    elif isinstance(response_data, dict):
                        print(f"✅ Response là DICT")
                        print(f"📋 Keys: {list(response_data.keys())}")
                        # Thử các khả năng response structure
                        video_url = (
                            response_data.get("webContentLink") or
                            response_data.get("webViewLink") or
                            response_data.get("video_url") or
                            response_data.get("url") or
                            response_data.get("videoUrl") or
                            response_data.get("file_url") or
                            response_data.get("downloadUrl")
                        )
                        video_name = response_data.get("name") or response_data.get("originalFilename")
                        print(f"🔗 Tìm thấy URL: {video_url}")
                        print(f"📝 Tìm thấy name: {video_name}")
                        
                        # Convert Google Drive view link to direct download
                        if video_url and "drive.google.com/file/d/" in video_url:
                            file_id = video_url.split("/file/d/")[1].split("/")[0]
                            print(f"🆔 Extracted file_id: {file_id}")
                            video_url = f"https://drive.google.com/uc?export=download&id={file_id}"
                            print(f"✅ Converted to direct download: {video_url}")
                    elif isinstance(response_data, str):
                        print(f"✅ Response là STRING")
                        video_url = response_data
                        print(f"🔗 URL: {video_url}")
                    else:
                        print(f"⚠️ Response type không xác định: {type(response_data)}")
                    
                    # Log video URL
                    print(f"\n📊 KẾT QUẢ TÌM KIẾM:")
                    if video_url:
                        print(f"✅ VIDEO URL: {video_url}")
                        print(f"✅ VIDEO NAME: {video_name}")
                    else:
                        print("❌ Không tìm thấy video URL trong response!")
                    print("="*80 + "\n")
                    
                    if video_url:
                        # Hiển thị thông tin video
                        st.markdown("### 🎬 Video đã được tạo!")
                        
                        if video_name:
                            st.info(f"📁 Tên file: **{video_name}**")
                        
                        # Hiển thị prompt đã dùng
                        st.info(f"💭 Prompt: {prompt}")
                        
                        # Tự động tải video về local để hiển thị
                        st.markdown("#### 📺 Xem Video:")
                        
                        try:
                            # Tạo filename
                            filename = video_name or f"video_{int(time.time())}.mp4"
                            if not filename.endswith('.mp4'):
                                filename += '.mp4'
                            
                            # Kiểm tra xem file đã tồn tại chưa
                            filepath = VIDEO_DIR / filename
                            
                            # Nếu file chưa tồn tại, hiển thị spinner khi tải
                            video_path = None
                            if not filepath.exists():
                                print(f"📥 File chưa tồn tại, đang tải từ: {video_url}")
                                # Sử dụng spinner và đảm bảo nó tự tắt khi xong
                                loading_placeholder = st.empty()
                                with loading_placeholder.container():
                                    with st.spinner("⏳ Đang tải video để hiển thị..."):
                                        video_path = download_video_from_url(video_url, filename)
                                # Clear spinner placeholder sau khi tải xong
                                loading_placeholder.empty()
                            else:
                                print(f"✅ File đã tồn tại: {filepath}")
                                video_path = str(filepath)
                            
                            # Hiển thị video sau khi đã tải xong (spinner đã tắt)
                            if video_path and os.path.exists(video_path):
                                # Hiển thị video từ local file với kích thước nhỏ hơn
                                print(f"🎬 Đang hiển thị video từ: {video_path}")
                                # Wrap video trong container để control size (rộng hơn)
                                video_col1, video_col2, video_col3 = st.columns([0.5, 5, 0.5])
                                with video_col2:
                                    st.video(video_path)
                                
                                # Hiển thị thông tin
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric("📁 Tên file", os.path.basename(video_path))
                                with col2:
                                    st.metric("📊 Kích thước", get_video_size(video_path))
                                
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
                                st.error("❌ Không thể tải video về. Vui lòng thử lại.")
                                st.info(f"🔗 Link video: {video_url}")
                        except Exception as e:
                            print(f"❌ Lỗi khi tải/hiển thị video: {str(e)}")
                            import traceback
                            print(traceback.format_exc())
                            st.error(f"❌ Lỗi: {str(e)}")
                            
                            # Thử hiển thị bằng iframe cho Google Drive
                            if "drive.google.com" in video_url:
                                st.markdown("**Thử xem video từ Google Drive:**")
                                # Extract file ID
                                if "/file/d/" in video_url:
                                    file_id = video_url.split("/file/d/")[1].split("/")[0]
                                    embed_url = f"https://drive.google.com/file/d/{file_id}/preview"
                                    st.markdown(f'<iframe src="{embed_url}" width="100%" height="480" allow="autoplay"></iframe>', unsafe_allow_html=True)
                                else:
                                    st.info(f"🔗 Link video: {video_url}")
                            else:
                                st.info(f"🔗 Link video: {video_url}")
                    else:
                        st.warning("⚠️ Không tìm thấy URL video trong response. Vui lòng kiểm tra n8n workflow.")
                        st.json(response_data)  # Hiển thị toàn bộ response để debug
    
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
                    
                    # Hiển thị video với kích thước rộng hơn
                    video_col1, video_col2, video_col3 = st.columns([0.5, 5, 0.5])
                    with video_col2:
                        st.video(str(video_path))
                    
                    st.markdown("---")

if __name__ == "__main__":
    main()
