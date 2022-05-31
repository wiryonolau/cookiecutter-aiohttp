from {{ cookiecutter.project_slug }}.app import app

def main():
    app(as_dev=False)

if __name__ == "__main__":
    main()
