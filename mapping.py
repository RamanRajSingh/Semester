def preprocess_input(form_data, active_sections):
    features = []

    # Section 1
    features.append(int(form_data['age']))
    features.append(form_data['gender'])  # one-hot or encoded
    # ... more fields from Section 1

    # Section 2
    # Add based on active_sections
    # Section 4, 5, 6 only if in active_sections

    # Example:
    if '4' in active_sections:
        features.append(int(form_data['years_at_company']))
        # ... any other sec-4 fields

    # Similarly handle section 5 and 6

    return features
