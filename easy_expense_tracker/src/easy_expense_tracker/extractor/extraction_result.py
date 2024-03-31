from datetime import datetime

class ExtractionResult:
    def __init__(self,
            timestamp : str,
            description : str,
            amount : float,
            cash_flow : str,
            doc_id : str,
            category : str,
            annotation : str,
            template : str):
        self.template=template
        self.timestamp=timestamp
        self.description=description
        self.amount=amount
        self.cash_flow=cash_flow
        self.doc_id=doc_id
        self.category=category
        self.annotation=annotation

    def __repr__(self):
        return '"' + ';'.join((
            datetime.fromtimestamp(self.timestamp).strftime("%d/%m/%Y"),
            self.description,
            str(self.amount),
            self.cash_flow,
            self.doc_id,
            self.category,
            self.annotation,
        )) + '"'
