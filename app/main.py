import sys
import logging

from .rag_pipeline import RAGPipeline
from .config import print_config_summary


# --------------------------------------------------
# Logging Configuration
# --------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --------------------------------------------------
# CLI Interface
# --------------------------------------------------

def run_cli():
    """
    Runs the command line AI assistant.
    """

    try:

        print_config_summary()

        # Initialize pipeline
        try:
            rag = RAGPipeline()
        except Exception as e:
            logger.error(f"Pipeline initialization failed: {e}")
            print("Failed to initialize AI assistant components.")
            sys.exit(1)

        print("\nHellobooks AI Assistant")
        print("Type your accounting question or type 'exit' to quit.\n")

        while True:
            try:

                user_question = input("Question: ").strip()

                # empty input guard
                if not user_question:
                    print("Please enter a valid question.\n")
                    continue

                # exit commands
                if user_question.lower() in ["exit", "quit"]:
                    print("Exiting assistant. Goodbye.")
                    break

                answer = rag.ask(user_question)

                print("\nAnswer:")
                print(answer)
                print("\n" + "-" * 50 + "\n")

            except KeyboardInterrupt:
                print("\nSession interrupted. Exiting safely.")
                break

            except EOFError:
                print("\nInput stream closed. Exiting.")
                break

            except Exception as e:
                logger.error(f"Error processing question: {e}")
                print("An error occurred while processing your request.\n")

    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        print("Failed to start the AI assistant.")
        sys.exit(1)


# --------------------------------------------------
# Program Entry Point
# --------------------------------------------------

if __name__ == "__main__":
    run_cli()