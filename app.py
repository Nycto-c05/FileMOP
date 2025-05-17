import streamlit as st
import os
import shutil
import subprocess
import sys
from pathlib import Path
import tempfile

# App configuration
st.set_page_config(
    page_title="FileMOP",
    page_icon="🗂️",
    layout="wide"
)

# Constants
UPLOAD_FOLDER = "files"
SCRIPT_NAME = "file_management.py"  # Your original script should be named this

def ensure_upload_folder():
    """Create the upload folder if it doesn't exist"""
    
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

def display_directory_tree(path, prefix="", is_last=True, show_root_files=False):
    """Display directory structure in a tree format"""
    if not os.path.exists(path):
        return []
    
    items = []
    try:
        entries = sorted(os.listdir(path))
        dirs = [e for e in entries if os.path.isdir(os.path.join(path, e)) and not e.startswith('.')]
        files = [e for e in entries if os.path.isfile(os.path.join(path, e)) and not e.startswith('.')]
        
        # For root level, only show directories unless show_root_files is True
        if prefix == "" and not show_root_files:
            entries_to_show = dirs
        else:
            entries_to_show = dirs + files
        
        for i, entry in enumerate(entries_to_show):
            entry_path = os.path.join(path, entry)
            is_last_entry = (i == len(entries_to_show) - 1)
            
            if is_last_entry:
                current_prefix = "└── "
                next_prefix = prefix + "    "
            else:
                current_prefix = "├── "
                next_prefix = prefix + "│   "
            
            if os.path.isdir(entry_path):
                items.append(f"{prefix}{current_prefix}📁 {entry}/")
                # For subdirectories, always show files
                items.extend(display_directory_tree(entry_path, next_prefix, is_last_entry, True))
            else:
                # Get file size
                size = os.path.getsize(entry_path)
                size_str = format_file_size(size)
                items.append(f"{prefix}{current_prefix}📄 {entry} ({size_str})")
    except PermissionError:
        items.append(f"{prefix}└── ❌ Permission denied")
    
    return items

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"

def run_file_management_script():
    """Run the file management script on the uploads folder"""
    try:
        # Get absolute path of the upload folder
        target_path = os.path.abspath(UPLOAD_FOLDER)
        
        # Run the script
        result = subprocess.run([
            sys.executable, SCRIPT_NAME, 
            "--target", target_path
        ], capture_output=True, text=True)
        
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    st.title("🗂️ FileMOP")
    st.subheader("File Management & Organization Platform")
    
    # Ensure upload folder exists

    ensure_upload_folder()
    
    # Check if the management script exists
    if not os.path.exists(SCRIPT_NAME):
        st.error(f"⚠️ File management script '{SCRIPT_NAME}' not found. Please ensure the script is in the same directory as this app.")
        st.info("💡 Save your file management script as 'file_management.py' in the same folder as this Streamlit app.")
        return
    
    # Create two columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Upload Files")
        
        # File uploader with drag and drop
        uploaded_files = st.file_uploader(
            "Drag and drop files here",
            accept_multiple_files=True,
            help="Upload multiple files to organize them automatically"
        )
        
        # Save uploaded files
        if uploaded_files:
            with st.spinner("Saving uploaded files..."):
                for uploaded_file in uploaded_files:
                    # Save file to uploads folder
                    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                st.success(f"✅ Successfully uploaded {len(uploaded_files)} file(s)!")
                # Don't rerun here - let user decide when to organize
    
    with col2:
        st.header("🧹 File Management")
        
        # Button to run file management
        if st.button("🚀 Run File Organization", type="primary"):
            with st.spinner("Running file management script..."):
                success, stdout, stderr = run_file_management_script()
                
                if success:
                    st.success("✅ File management completed successfully!")
                    if stdout:
                        st.text("Output:")
                        st.code(stdout)
                    # Set flag to show directory structure
                    st.session_state.show_structure = True
                    st.rerun()  # Refresh to show updated directory structure
                else:
                    st.error("❌ Error running file management script")
                    if stderr:
                        st.error(f"Error details: {stderr}")
    
    # Display directory structure only after file organization is run
    if 'show_structure' in st.session_state and st.session_state.show_structure:
        st.header("📁 File Structure After Organization")
        
        # Check if files folder has content
        if os.path.exists(UPLOAD_FOLDER) and os.listdir(UPLOAD_FOLDER):
            tree_items = display_directory_tree(UPLOAD_FOLDER)
            if tree_items:
                st.text("files/")
                for item in tree_items:
                        st.text(item)
            else:
                st.info("📝 No files found in the directory")
        else:
            st.info("📝 The files directory is empty after organization")
    
    # Show log file if it exists
    if os.path.exists("file_management_log.csv"):
        st.header("📊 Management Log")
        if st.button("📋 View Log File"):
            try:
                import pandas as pd
                df = pd.read_csv("file_management_log.csv")
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"Error reading log file: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown("*FileMOP - Making file management simple and automated*")

if __name__ == "__main__":
    main()