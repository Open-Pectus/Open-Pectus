import os
print(os.listdir(os.getcwd()))

import uvicorn

from main import app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8300)
