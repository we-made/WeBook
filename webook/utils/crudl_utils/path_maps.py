class SectionCrudlPathMap:
    def __init__(self, detail_url, create_url, edit_url, delete_url, list_url) -> None:
        self.detail_url = detail_url
        self.create_url = create_url
        self.edit_url = edit_url
        self.delete_url = delete_url
        self.list_url = list_url

    create_url = None
    edit_url = None
    delete_url = None
    list_url = None