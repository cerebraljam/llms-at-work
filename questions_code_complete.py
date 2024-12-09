from llm_code import find_content


def prepare_questions(profile):
    company = profile.get("company")
    product = profile.get("product")

    return [
        {
            "goal": "The team performing the assessment isn't necessarily aware of what this service is doing. This question will tell them what the product is supposed to do, how it is supposed to be used, and what kind of data it is supposed to process.",
            "main": f"What is the purpose of '{product}' by '{company}'? Which problem is it promising to solve? Why would a customer consider using it?",
            "expected": "A brief description",
        },
        {
            "goal": "A service can be used by different types of users, such as administrators, end-users, or developers. This question will help the team understand who is the target market, operators, and users of the service.",
            "main": f"Who is the target market, operators and users of {company} {product}?",
            "expected": "A brief description",
        },
        {
            "goal": "The team needs to understand the key features of the service to assess the risks associated with it. This question will help the team understand what the service is supposed to do.",
            "main": f"What are the key features of {company} {product}?",
            "expected": "A list of features",
        },
        {
            "goal": f"The team can evaluate the potential inherent risks associated with a product based on its category. Pick your answer(s) from the following list, separate multiple categories with a comma, and only list the categories: Cloud monitoring, Cloud provider, Collaboration, Customer support, Data analytics, Data storage and processing, Document management, Employee management, Engineering, Finance and payments, Identity provider, IT, Marketing, Office operations, Other, Password management, Product and design, Professional services, Recruiting, Sales, Security, Version control. If the service doesn't fit one of these categories, answer: Other.",
            "main": f"What category of product is {company} {product} in?",
            "expected": "A list of categories",
        },
        {
            "goal": "Knowing what kind of companies or customers are using the product can help the team evaluate the maturity level of the product",
            "main": f"What is the list of companies or customers who are using {company} {product}?",
            "expected": "A list of companies or customers",
        },
        {
            "goal": "Where the service is hosted can have an impact on the data privacy and security of the service. This question will help the team understand where the service is hosted, and if there could be any legal or public image implications.",
            "main": f"Which Cloud Service Providers is {company} {product} using?",
            "label": "Cloud Service Providers",
            "function": find_content,
            "parameter": "Cloud Service Providers",
            "followup": [
                f"Where are 'PLACEHOLDER' hosting infrastructure located? official sources"
            ],
        },
        {
            "goal": "Where the service is hosted can have an impact on the data privacy and security of the service. This question will help the team understand where the service is hosted, and if there could be any legal or public image implications.",
            "main": f"Based on official documentation and Cloud Service Providers used, in which countries is {company} {product} hosted?",
            "label": "Cloud Service Providers",
            "expected": "A list of countries",
        },
        {
            "goal": "A service could be using third-party providers to process data. Laws and regulations requires companies to disclose the list of sub-processors. This question will help the team understand who are the sub-processors of the service.",
            "main": f"What is the list of sub-processors that {company} {product} is using?",
            "label": "Sub-Processors",
            "function": find_content,
            "parameter": "Sub-Processors",
            "followup": [
                f"Where are 'PLACEHOLDER' infrastructure geolocated? official sources"
            ]
            + [
                f"What kind of processing is PLACEHOLDER expected to do for {company} {product}?"
            ],
        },
        {
            "goal": "Depending on the type of service offered, different type of access to data might be necessary. For example, slack tools will need to be connected to Slack. Authentication tools will likely need to be connected to our HR system to get the list of employees, sales tools will likely need to have access to our CRM emails or calendards, CI/CD tools will likely need access to our code repositories. This question will help the team understand what kind of access rights are necessary to integrate the service with our existing infrastructure.",
            "main": f"Describe how {company} {product} is typically implemented and integrated into an organization's a existing infrastructure.",
            "label": "Connected Infrastructure",
            "function": find_content,
            "parameter": "Connected Infrastructure like tools, cloud service providers or products",
            "followup": [
                f"What are the access rights necessary to integrate {company} {product} with PLACEHOLDER? Are any of these access rights are Admin level?",
                f"How is the integration between {company} {product} and PLACEHOLDER typically managed? Is it done through a web interface, API, or other means? If so, what authentication rights are necessary?",
                f"What type of data should be expected to be shared between {company} {product} and PLACEHOLDER? (for example: Google Drive: company files, Slack: messages, etc.)",
                f"What is the expected quantity of data that will be shared between {company} {product} and PLACEHOLDER? (for example: some data, a significant amount, all data, etc.)",
            ],
        },
        {
            "goal": "We are expected to keep track of where personal data is stored and processed. This question will help the team understand if this service is going to process any PII, PHI, or other personal data.",
            "main": f"Based on the privacy policy, is {company} {product}'s purpose is to process Customer PII, Employee PII, Personal Health Information or other personal data? If so, what type of personal data is expected to be processed? Be specific.",
            "label": "Privacy",
            "expected": "A list of type of personal data",
        },
        {
            "goal": "Privacy laws require us to disclose how personal data is going to be used. This question will help the team understand how data will be used.",
            "main": f"Based on the privacy policy, is data going to be sent to third parties? If so, will the data be anonymized or pseudonymized before being sent?",
            "label": "Privacy",
            "expected": "A brief description",
        },
        {
            "goal": "Privacy laws require us to disclose how personal data is going to be used. This question will help the team understand the purpose of any personal data transfer.",
            "main": f"Based on the privacy policy, will the personal data be used for purposes other than providing the service? If so, what are the purposes?",
            "label": "Privacy",
            "expected": "A brief description",
        },
        {
            "goal": "Mature companies will normally be transparent about how they are using personal data. They will also require their subcontractors and partners to adhere to the same level of privacy. This question will help the team understand if there is a contractual agreement between the company and partners that ensures that personal data will not be mishandled.",
            "main": f"Based on the privacy policy, is there a contractual agreement between {company} and partners that ensures that personal data will not be mishandled?",
            "label": "Privacy",
            "expected": "A brief description",
        },
        {
            "goal": "Sub-contractors should stop using any data sent to them if we decide to stop using the service. This question will help the team understand if the data will be returned or deleted if we decide to stop using the service.",
            "main": f"Based on the privacy policy, if we decided to stop using {company}, will our data sent to partners be returned or deleted?",
            "label": "Privacy",
            "expected": "A brief description",
        },
        {
            "goal": "Sub-contractors should stop using any data sent to them if we decide to stop using the service. This question will help the team understand if the data will be returned or deleted if we decide to stop using the service.",
            "main": f"Based on the privacy policy, if we decided to stop using {company}, will our data be returned or deleted?",
            "label": "Privacy",
            "expected": "A brief description",
        },
        {
            "goal": "The idea is to understand how long the data will be stored. Some service will not store our data after processing, some other will store it for a limited time, and some other will store it indefinitely. This question will help the team understand how long the data will be stored.",
            "main": f"Based on the privacy policy, is there a data retention policy in place? If so, what is the retention period for personal data and log data?",
            "label": "Privacy",
            "expected": "A brief description",
        },
        {
            "goal": "In case of a data leakage incident, the company should notify us. This question will help the team understand how we will be notified",
            "main": f"Based on the privacy policy, if a data breach occurs, how will {company} notify the customers?",
            "label": "Privacy",
            "expected": "A brief description",
        },
        {
            "goal": "Some countries require companies to disclose if they received a request from the government to disclose personal data. This question will help the team understand how we will be notified if such a request is received.",
            "main": f"Based on the privacy policy, if there is a request from the government, municipality, or other public institution to disclose personal data, how will {company} notify us?",
            "label": "Privacy",
            "expected": "A brief description",
        },
        {
            "goal": "Privacy laws like the GDPR require companies to have a Data Protection Officer (DPO). If the company is following these laws, the name and contact details of the DPO should be public. If it should be public but isn't, this could be a red flag.",
            "main": f"What is the name and contact information of the Data Protection Officer (DPO) of {company}?",
            "label": "Privacy",
            "expected": "The name and contact information of the Data Protection Officer",
        },
        {
            "goal": "We are expected to keep track of where business sensitive data is stored and processed. This question will help the team understand if this service is going to process any financial information, intellectual property, vulnerability information, or other business sensitive data.",
            "main": f"Is {company} {product}'s purpose is to process Financial Information, Intellectual Property, vulnerability information, or other business sensitive data? If so, what type of business sensitive data is expected to be processed?",
            "label": "Data",
            "expected": "A brief description",
        },
        {
            "goal": "Our internal policy requires services to be integrated with our Single Sign-On (SSO) solution. This question will help the team understand if the service supports SSO.",
            "main": f"If employees are going to authenticate to {company} {product}, what are the authentication methods available? Is there a Single Sign-On (SSO) option available?",
            "label": "Authentication",
            "expected": "A list of authentication methods supported, and services it can be integrated with",
        },
        {
            "goal": "The team is using the list of laws and regulations that a company is claiming to be compliant with to evaluate the potential risks associated with the service. We are particularly interested into the following: GDPR (European Union), CCPA/CPRA (California, USA), APPI (Japan), PDPA (Singapore), PIPA (South Korea), PDPA (Taiwan), HIPAA (USA, healthcare), Sarbanes-Oxley Act (USA, public companies), Gramm-Leach-Bliley Act (USA, financial institutions), NIS Directive (European Union), PIPL (China), Federal Information Security Management Act (FISMA) (USA, federal agencies), Cybersecurity Law of the People's Republic of China, Network and Information Systems Regulations (UK), Cyber Security Act (Singapore), Act on the Protection of Personal Information (South Korea), Digital Security Act (European Union), SHIELD Act (New York, USA), Cybersecurity Maturity Model Certification (CMMC) (USA, Defense contractors)",
            "main": f"According to the Trust Center page, or the official site, what laws and regulations is {company} {product} compliant with?",
            "label": "Compliance",
            "expected": "A list of laws and regulations",
        },
        {
            "goal": "The team is using the list of compliance standards that a company is claiming to be compliant with to evaluate the potential risks associated with the service. We are particularly interested into the following: ISO/IEC 27001, SOC 2, PCI DSS, HITRUST CSF, COBIT, NIST Cybersecurity Framework, CIS Controls, FISMA, FedRAMP",
            "main": f"According to the Trust Center page, or the official site, what compliance standards is {company} {product} following?",
            "label": "Compliance",
            "expected": "A list of compliance standards",
        },
        {
            "goal": "The team is using the list of security standards that a company is claiming to follow to evaluate their potential maturity level. We are particularly interested into the following: NIST SP 800-53, ISO/IEC 27002, OWASP Top 10, CIS Benchmarks, SANS Critical Security Controls, CSA Cloud Controls Matrix, ETSI Cyber Security Standards, IEC 62443 (Industrial Control Systems), FIPS 140-2/140-3",
            "main": f"According to the Trust Center page, or the official site, what security standards is {company} {product} compliant with?",
            "label": "Compliance",
            "expected": "A list of security standards",
        },
        {
            "goal": "The maturity of a company can be evaluated based on the number of security engineers they have. This question will help the team understand how much effort is put into security.",
            "main": f"Based on {company}'s the career site, what kind of profile of security engineers are they looking for? How many security engineers are currently working at {company}?",
            "label": "Maturity",
            "expected": "A brief description",
        },
        {
            "goal": "The maturity of a company can be evaluated based on the number of security engineers they have. This question will help the team understand how much effort is put into security. It is ok not to limit searches on the company websites for this question.",
            "main": f"What is the name of the CISO at {company}? Is the CISO publishing blog articles or speaking at conferences?",
            "label": "Maturity",
            "expected": "A brief description",
        },
        {
            "goal": "The maturity of a company can be evaluated based on the number of security engineers they have. This question will help the team understand how much effort is put into security. It is ok not to limit searches on the company websites for this question.",
            "main": f"Based on {company}'s blog, are the security team members at {company} posting blog posts, speaking at conferences, or contributing to open-source projects?",
            "label": "Maturity",
            "expected": "A brief description",
        },
        {
            "goal": "Depending on the nature of service offered by the company, the impact of an outage can vary. This question will help the team understand what is the expected impact on our customers or internal operations if the service is suffering from an outage.",
            "main": f"If {company} {product} is suffering from an outage, what is the expected impact on the customer? How is the customer notified of the outage?",
            "label": "Maturity",
            "expected": "A brief description",
        },
        {
            "goal": "The team is using the list of previously disclosed security incidents to evaluate the potential risks associated with the service. A company that delayed the disclosure of a security incident could be a red flag.",
            "main": f"Is there a list of known security incidents in which {company} {product} was involved? What was the impact of these incidents on the customers?",
            "label": "Maturity",
            "expected": "A brief description",
        },
        {
            "goal": "The intellectual property team want to be sure that we will not be infringing any third-party intellectual property rights by using this service. This question will help the team understand if any model trained from potentially copyrighted content is being used to produce any output we would end up publishing.",
            "main": f"Is {company} {product} a product that will use Generative AI, Natural Language Processing, LLM or other AI technologies? If so, how are these technologies used?",
            "label": "AI",
            "expected": "A brief description",
        },
        {
            "goal": "In order to evaluate the risks of supply chain attacks, the team is trying to understand if the service is completely or partially outsourced to partners or contractors.",
            "main": f"Based on the privacy policy, is development, maintenance and/or operation of the service completely or partially outsourced to partners or contractors? If so, which ones? Exclude Cloud Service Providers, we are looking for consulting firms.",
            "label": "Privacy",
            "function": find_content,
            "parameter": "Partners or contractors",
            "followup": [
                f"Is 'PLACEHOLDER' located outside of Japan or the US?",
            ],
        },
        {
            "goal": "Depending on the criticality of the service, the team might want to know if the service includes audit logging.",
            "main": f"Does the service include audit logging? If so, what kinds of events are logged? (e.g., user logins, user activities, system changes, data access)",
            "label": "Audit Logging",
            "expected": "A list of events that are logged",
        },
        {
            "goal": "Depending on the criticality of the service, the team might want to know if the service includes audit logging.",
            "main": f"Can audit logs from {product} be exported or integrated with a SIEM solution? If so, how? Is log streaming to a SIEM or other log management platform is supported? What formats are supported (e.g., JSON, syslog, protobuf)?",
            "label": "Audit Logging",
            "expected": "A brief description",
        },
        {
            "goal": "Depending on the criticality of the service, the team might want to know if the service includes audit logging.",
            "main": f"Is there a retention policy for auditing logs? if so, how long are logs stored, and can this retention period be adjusted?",
            "label": "Audit Logging",
            "expected": "A brief description",
        },
    ]
