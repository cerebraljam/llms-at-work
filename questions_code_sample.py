def prepare_questions(profile):
    company = profile.get("company")
    product = profile.get("product")

    # Short list of questions for the demonstration. See questions_code_complete.py for a longer list.
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
            "goal": f"The team can evaluate the potential inherent risks associated with a product based on its category. Pick your answer(s) from the following list, separate multiple categories with a comma, and only list the categories: Cloud monitoring, Cloud provider, Collaboration, Customer support, Data analytics, Data storage and processing, Document management, Employee management, Engineering, Finance and payments, Identity provider, IT, Marketing, Office operations, Other, Password management, Product and design, Professional services, Recruiting, Sales, Security, Version control.",
            "main": f"What category of product is {company} {product} in?",
            "expected": "A list of categories",
        },
        {
            "goal": "Knowing what kind of companies or customers are using the product can help the team evaluate the maturity level of the product",
            "main": f"What is the list of companies or customers who are using {company} {product}?",
            "expected": "A list of companies or customers",
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
    ]
