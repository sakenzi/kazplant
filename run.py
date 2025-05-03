import uvicorn


if __name__ == "__main__":
    uvicorn.run("main:app", host="192.168.253.36", port=8000, reload=True)