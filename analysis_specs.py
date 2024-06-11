import textwrap
import google.generativeai as genai

clause_types = [
    "Recital Clauses",
    "Definition Clauses",
    "Payment Clauses",
    "Performance Clauses",
    "Confidentiality Clauses",
    "Indemnity Clauses",
    "Limitation of Liability Clauses",
    "Termination Clauses",
    "Force Majeure Clauses",
    "Dispute Resolution Clauses",
    "Entire Agreement Clauses",
    "Severability Clauses"
]

types_of_contracts = [
    "Service Contract",
    "Sales Contract",
    "Lease Agreement",
    "Employment Contract",
    "Non-Disclosure Agreement (NDA)",
    "Partnership Agreement",
    "Indemnity Agreement",
    "Franchise Agreement",
    "Licensing Agreement",
    "Supply Contract",
    "Construction Contract",
    "Joint Venture Agreement",
    "Merger and Acquisition Agreement (M&A)",
    "Shareholder Agreement"
]
alert_types = [
    "Payment Alert",
    "Invoice Alert",
    "Contract Expiry Alert",
    "Contract Start Alert",
    "Compliance Alert",
    "Performance Review Alert",
    "Maintenance Alert",
    "Meeting Alert",
    "Deadline Alert",
    "Policy Update Alert",
    "Billing Alert",
    "Legal Alert",
    "Training Alert",
    "Audit Alert",
    "Customer Feedback Alert",
    "Inventory Alert",
    "Security Alert"
]

alert = genai.protos.Schema(
    type=genai.protos.Type.OBJECT,
    properties={
        'name': genai.protos.Schema(type=genai.protos.Type.STRING, description="The name of the alert."),
        'type': genai.protos.Schema(type=genai.protos.Type.STRING, enum=alert_types, description="The type of the alert. It can be either Payment Reminder or Renewal Reminder."),
        'due_date': genai.protos.Schema(type=genai.protos.Type.STRING, description="The due date of the alert in YYYY-MM-DD format."),
        'amount': genai.protos.Schema(type=genai.protos.Type.STRING, description="The amount associated with the alerts. If the amount is not available, return N/A."),
        'details': genai.protos.Schema(type=genai.protos.Type.STRING, description="Detailed information about the alerts."),
    },
    required=['name', 'type', 'due_date', 'amount', 'details']
)

alerts = genai.protos.Schema(
    type=genai.protos.Type.ARRAY,
    items=alert
)

clause = genai.protos.Schema(
    type=genai.protos.Type.OBJECT,
    properties={
        'type': genai.protos.Schema(type=genai.protos.Type.STRING, enum=clause_types),
        'description': genai.protos.Schema(type=genai.protos.Type.STRING, description="Give a detailed description of the clause. The description must contain all details from the clause."),
        'financial_info': genai.protos.Schema(type=genai.protos.Type.STRING, description="Return the financial information in this format: if the business is making money from this clause: Gain-$100,000 or if it is losing money or paying for salary or an entity: Loss-$100,000. If the information is not available, return N/A"),
    },
    required=['type', 'description', 'financial_info']
)

clauses = genai.protos.Schema(
    type=genai.protos.Type.ARRAY,
    items=clause
)

Contract_category = genai.protos.Schema(
    type=genai.protos.Type.OBJECT,
    properties={
        'title': genai.protos.Schema(type=genai.protos.Type.STRING, description="Give a title that best describes and summarizes the contract. The title must contain some details from the contract that best describe it"),
        'summary': genai.protos.Schema(type=genai.protos.Type.STRING, description="Give a summary of the contract. The summary must contain main details from the contract that best describe it. Make it in bullet points and ensure it is not more than 100 words"),
        'type': genai.protos.Schema(type=genai.protos.Type.STRING, enum=types_of_contracts),
        'start_of_contract': genai.protos.Schema(type=genai.protos.Type.STRING, description="Return the date in this format: YYYY-MM-DD. If the date is not available, return 0"),
        'end_of_contract': genai.protos.Schema(type=genai.protos.Type.STRING, description="Return the date in this format: YYYY-MM-DD. If the date is not available, return 0"),
        'clauses': clauses,

    },
    required=['title', 'summary', 'type', 'start_of_contract', 'end_of_contract', 'clauses', 'payment_reminder', 'renewal_reminder']
)

analyze_contract = genai.protos.FunctionDeclaration(
    name="analyze_contract",
    description=textwrap.dedent("""\
        Analyze this contract. Each clause should be analyzed in detail and should not miss any information. 
        Additionally, extract and return information about payment alerts and renewal alerts.
    """),
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={
            'clauses': clauses,
            'Contract_category': Contract_category,
        }
    )
)

analyze_alerts = genai.protos.FunctionDeclaration(
    name="analyze_alerts",
    description=textwrap.dedent("""\
        Analyze alerts. alerts are important for the business to keep track of payments and renewals.
        Each alert should be analyzed in detail and should not miss any information.
    """),
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={
            'alerts': alerts,
        }
    )
)