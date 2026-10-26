# Loads the slide content for build.py and check.py: content.py here by default,
# or the file named in $SERIES_CONTENT (for example series/linkedin/content.py).
import importlib.util, os


def load_content():
    path = os.environ.get("SERIES_CONTENT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "content.py"))
    spec = importlib.util.spec_from_file_location("series_content", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
