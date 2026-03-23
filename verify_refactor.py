import sys
import os

# Add the current directory to sys.path
sys.path.append(os.getcwd())

try:
    from asset_optimizer import optimize_images, optimize_audio
    print("✅ Successfully imported optimize_images and optimize_audio from asset_optimizer")
    
    # Mock check
    print(f"optimize_images is callable: {callable(optimize_images)}")
    print(f"optimize_audio is callable: {callable(optimize_audio)}")

except ImportError as e:
    print(f"❌ ImportError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ An error occurred: {e}")
    sys.exit(1)

sys.exit(0)
