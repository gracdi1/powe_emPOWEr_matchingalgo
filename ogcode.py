import pandas as pd
from collections import defaultdict

# Sample mentees and mentors DataFrames
mentors_df = pd.read_excel("(Mentor) Shadow Day Sign Up (2023-2024) (Responses).xlsx") #change the name of the file and upload the file directly into the folder, same level as this file
mentees_df = pd.read_excel("(Mentee) Shadow Day Sign Up (2023-2024) (Responses).xlsx") #same here

mentor_replacement_mapping = {
    "First": "mentor_name",
    "Major": "engineering",
    "language": "mentor_language",
    "student": "max_mentee"
}

mentee_replacement_mapping = {
    "Last": "mentee_name",
    "Major": "interest",
    "language": "language",
    "Email Address": "email",
    "expect": "expectations"
}

for column_name in mentors_df.columns:
    for word_to_find, new_word in mentor_replacement_mapping.items():
        if word_to_find in column_name:
            mentors_df.rename(columns={column_name: column_name.replace(column_name, new_word)}, inplace=True)

for column_name in mentees_df.columns:
    for word_to_find, new_word in mentee_replacement_mapping.items():
        if word_to_find in column_name:
            mentees_df.rename(columns={column_name: column_name.replace(column_name, new_word)}, inplace=True)

mentees_df['interest'] = mentees_df['interest'].str.split(', ')

# Initialize mentor-mentee mapping
mentor_mentee_mapping = defaultdict(list)
unmatched_mentees = []

# Iterate through mentees and try to match them with mentors
for mentee_row in mentees_df.itertuples():
    mentee = mentee_row._asdict()
    print(mentee['mentee_name'])
    best_mentor = None
    min_mentee_count = float('inf')

    for mentor_row in mentors_df.itertuples():
        mentor = mentor_row._asdict()

        # Check if the mentor's language matches the mentee's language or the mentor is bilingual
        if mentor["mentor_language"] == mentee["language"] or mentee["language"] == "Bilingual" or mentor["mentor_language"] == "Bilingual":
            # Check if the mentor covers at least one of the mentee's fields
            common_fields = set(mentee["interest"]).intersection([mentor["engineering"]])
            # print(mentee["interest"].dtype)
            # print(mentor["engineering"].dtype)
            # print(common_fields)
            if common_fields:
                # print("there were common fields")
                # Check if the mentor has the minimum mentee count
                if len(mentor_mentee_mapping[mentor["mentor_name"]]) < mentor["max_mentee"]:
                    # Update the best mentor if the current mentor has fewer mentees
                    if len(mentor_mentee_mapping[mentor["mentor_name"]]) < min_mentee_count:
                        min_mentee_count = len(mentor_mentee_mapping[mentor["mentor_name"]])
                        best_mentor = mentor["mentor_name"]
                        # print(f'her best mentor is {best_mentor}')

    # Add mentee to the best mentor's list
    if best_mentor is not None:
        mentor_mentee_mapping[best_mentor].append(mentee["mentee_name"])
    else:
        unmatched_mentees.append(mentee["mentee_name"])

result_list = []

for mentor, mentees in mentor_mentee_mapping.items():
    result_list.append({"Mentor": mentor, "Mentees": ', '.join(mentees)})

# Add unmatched mentees to the results
for mentee in unmatched_mentees:
    result_list.append({"Mentor": "Unmatched", "Mentees": mentee})

# print(result_list)

# Create a new DataFrame from the list of results
results_df = pd.DataFrame(result_list, columns=["Mentor", "Mentees"])

merged_df = pd.merge(results_df, mentors_df, left_on='Mentor', right_on='mentor_name', how='left')
cleaned_df = merged_df[['Mentor', 'Mentees']]

def create_email(row):
    template = f"""
Hi {row['MentorName']}!

POWE would like to thank you for volunteering for this amazing program, and are pleased to inform you that you have been matched with a mentee! You can find your mentee's name and contact information below: 

If you have been matched with multiple mentees, you will receive multiple emails from POWE in your inbox with different contact information for each mentee!

Name: {row['MenteeName']}
Email Address: {row['email']}
Engineering fields of interest: {row['interest']}

One of POWE’s mandates is to increase the number of women and minorities in engineering. Through the Shadow Days program, our aim is to encourage high school and CEGEP students to see what life in engineering is like, specifically for women, and to hopefully encourage them to pursue their education in this field.

As a POWE volunteer, we encourage you to play a supportive and informative role for these young students and make them feel welcome as at this point, you not only represent McGill but also the engineering profession and they will look up to you for inspiration and encouragement. 

Please note that you are responsible for contacting your mentee(s) as soon as possible, but given the current timeline, do consider concentrating on studying for your finals! Ideally, you would have your first contact with your mentee before the end of the semester.

Feel free to introduce yourself, your program, extracurriculars, and hobbies. You can also ask them to move to a communication platform that is more convenient for the both of you (it may be easier and more casual to stay in contact via Facebook, Instagram, etc…). If you have multiple mentees, you can even make a group chat!

We encourage you to set up at least 1 video call or in-person meet-up throughout the semester. You can also give them the full Shadow Days experience by inviting them for an on-campus tour or even taking them to class with you if you are comfortable with that! We hope that beyond mentors and mentees, you come out with a new friend at the end of this mentorship program! 

We have listed below some topics to talk about, but feel free to talk about anything else that your mentee might be interested in. This is just meant to give you some pointers in case you have difficulty connecting with your mentee!

            ·    	What is your schedule like?
            ·    	Difficulty level of your classes and how it varies 
            ·    	Minor concentrations/different streams within engineering
            ·    	Research or internships you have done
            ·    	Your class projects
            ·    	How to get involved in engineering as well as non-engineering clubs 
            ·    	Helpful resources available (Engineering Peer Tutoring Service, TAs, McGill Engineering Student Centre)
            ·    	How to deal with stress (Peer Support Center, McGill Counseling services)
            ·   	Be optimistic! What does a semester in engineering at McGill look like?

These were the expectations that they noted in their form:
'{row['expectations']}'

If you have any questions or concerns about the program, feel free to email us at this email. We hope you and your mentee will have a good time and that it will be a fulfilling experience for both of you! 

Best,
            """
    if row['MenteeName']:
        return template
    else:
        return

# Create a new DataFrame for the results
mentee_result_list = []

# Add matched mentee-mentor pairs to the results
for mentor, mentees in mentor_mentee_mapping.items():
    for mentee in mentees:
        # print(f'the mentor is {mentor} and the mentee is {mentee}')
        mentee_result_list.append({"MenteeName": mentee, "MentorName": mentor})

# print(mentee_result_list)
# Add unmatched mentees to the results
for mentee in unmatched_mentees:
    mentee_result_list.append({"MenteeName": mentee_row.mentee_name, "MentorName": "Unmatched"})

# Create a new DataFrame from the list of results
mentee_results_df = pd.DataFrame(mentee_result_list, columns=["MenteeName", "MentorName"])
# print(mentee_results_df.columns)
mentor_merge_df = pd.merge(mentee_results_df, mentors_df, left_on='MentorName', right_on='mentor_name', how='left')
mentee_merged_df = pd.merge(mentor_merge_df, mentees_df, left_on='MenteeName', right_on='mentee_name', how='left')

print(mentee_merged_df.columns)

new_df = mentee_merged_df[['MenteeName', 'MentorName', 'email', 'interest', 'engineering', 'language', 'expectations']]

new_df = new_df.assign(template=new_df.apply(create_email, axis=1))

# Save the results to an Excel file
new_df.to_excel("mentee_matching.xlsx", index=False)
