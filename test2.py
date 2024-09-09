from prefect import flow

@flow
def my_flow():
    print("Running my flow!")

if __name__ == "__main__":
    my_flow.serve()
