import argparse
from tqdm import tqdm
from huggingface_hub import HfApi


class HFActivator:
    def __init__(self, tokens: str):
        self.tokens = tokens.split(";")
        self.api = HfApi()

    def _parse_authors(self, token: str):
        names = [self.api.whoami(token=token)["name"]]
        orgs = self.api.get_user_overview(username=names[0]).orgs
        for org in orgs:
            names.append(org.name)

        return names

    def _list_sleeping_spaces(self, token: str):
        sleeping_spaces = []
        authors = self._parse_authors(token)
        for author in authors:
            spaces = self.api.list_spaces(author=author, token=token)
            for space in tqdm(spaces, desc=f"Filtering {author} spaces"):
                space_stage = self.api.get_space_runtime(space.id, token=token).stage
                if space.sdk == "gradio" and space_stage == "SLEEPING":
                    sleeping_spaces.append(space.id)

        return sleeping_spaces

    def _activate_spaces(self):
        activated_spaces = []
        for token in self.tokens:
            sleeping_spaces = self._list_sleeping_spaces(token)
            for space_id in sleeping_spaces:
                self.api.restart_space(space_id, token=token)

            activated_spaces += sleeping_spaces

        if activated_spaces:
            print(", ".join(activated_spaces) + " activated!")
        else:
            print("No sleeping space found...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Activate HF spaces")
    parser.add_argument("--tokens", required=True, help="Your HF Access Tokens")
    args = parser.parse_args()
    HFActivator(args.tokens)._activate_spaces()
