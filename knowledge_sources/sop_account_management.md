# IndiGo BluChip SOP — Membership Account Management (V4.0)

> Operational agent SOP. Source: sop.docx (V4.0). Covers profile updates, account merge, transfer-on-death, account/tech issues, travel-doc discrepancies, policy disputes, tier upgrade/retention, BluChips expiry, fraud, and account deletion. (The source also has 200 flowchart/screenshot images that are not captured as text here.)

## Version control

Revision Num- ber | Date | Author | Description of Changes | Reviewed By | Approved By
1.0 | 28-Aug-24 | Vikas Yadav | Initial draft | Vikas Yadav | -
2.0 | 05-Sep-24 | Alok Mishra/ Vikas Yadav | Major edits and updates | Vikas Yadav | -
3.0 | 16-Sep-24 | Alok Mishra | Minor edits and updates | Vikas Yadav | -
4.0 | 10-Dec-25 | Mahima Nayyar | SOP guidance as per new issue categories | Alok  Mishra/Mahima | Vikas Yadav
Index

## 1. Account information Enquiry

## 1. Account/Transaction details

*Scenario:* Account information like Profile Details, Membership no., IndiGo BluChip  Balance and Transaction details    → How to check member account details (FFN No. tier details, flight milestone) on, transaction details LMS  → How member can view IBC account details on the dashboard?

**SOP — steps:**
Profile info flow on LMS/Member care portal                                      Profile info flow on 6E website
Profile information flow on LMS/Member care
Step -1: Open the LMS portal and Click on the “Sign in with SSO” Note – LMS can be accessed from Salesforce also.
Step –2: Enter your Lan Id/Email-ID and Click on the “Next” option.
Step – 3: Click on the Menu (Nine Dots) upper left corner
Step 4: Click the drop–down menu “Member Care”.
Step –5: Enter “FF Number” or Loyalty registered Email ID” >>> Click on “Search”
Step –6: Click on “Loyalty” and Check the Tier Status.
Profile information flow on 6E website
Member will be able to view their profile details – Membership no, IBC balance, Transaction details under the “Dashboard” section. For nominee details Click on “My Nominees”
2.  Update profile details

## 2a. Name Update request

*Scenario:* Member requesting to update name in the account

Name Update | Old  Name | New Name | Remarks

**Screen reference — Compare Profile Details - Edit CP First Name (Customer Profile Details):**

UI screenshot of a Salesforce-style case record showing the "Details" tab with a "Compare Profile Details" panel and a "Customer Profile Details" edit section.

What the screen shows:
1. Tabs at top: Feed | Details (active) | Related.
2. "Compare Profile Details" panel lists the same member's profile across three source systems side by side:
   - CIAM: Api Status = Success, First Name = Vikas, Last Name = Kumar Yadav, Gender = Male, Date of Birth = 1976-11-24, Mobile No. = 9810075469, Email = rhlsaxena7@gmail.com, Email Verified = true, Mobile Verified = true.
   - Navitaire: Api Status = Success, First Name = Vikas, Last Name = Kumar Yadav, Gender = Male, Date of Birth = 1976-11-24, Mobile No. = +919810075469, Email = rhlsaxena7@gmail.com.
   - Capillary: Api Status = Success, First Name = Vikas, Last Name = Kumar Yadav, Gender = Male, Date of Birth = 1976-11-24, Mobile No. = 919810075469, Email = rhlsaxena7@gmail.com.
3. Below is a "Customer Profile Details" section (outlined in red) with editable fields, each having a pencil edit icon: CP First Name, CP Last Name, CP DOB, CP Gender, Type of Changes, No of Changes (= 0), Expert Status, Email Body.

Action for the agent:
- Click the pencil (edit) icon next to "CP First Name" (highlighted in red) to enter/update the customer's first name in the Customer Profile Details section.

**Screen reference — Salesforce Case - Compare Profile Details / Submit for Approval (Name Change):**

UI screenshot: Salesforce Case record (Case 21883878, Status: Open) for a Name Change Request, showing the "Compare Profile Details" comparison and how to submit it for approval.

Actions / what the agent should do:
1. Top-right action bar has buttons: "Send Upload File Link", "Fetch PNR Detail", "Fetch Mobile PNR", and a dropdown arrow.
2. Click the dropdown arrow (highlighted) to expand more actions: "Change Owner", "Edit", and "Submit for Approval".
3. Click "Submit for Approval" (highlighted in red) to route the case for approval.

Case header fields: Status = Open; Loyalty Tier, Member Type, Loyalty Number (blank in view).

Tabs: Feed | Details (selected) | Related.

"Compare Profile Details" table comparing three systems (CIAM / Navitaire / Capillary):

| Field | CIAM | Navitaire | Capillary |
|---|---|---|---|
| Api Status | Success | Success | Success |
| First Name | Vikas | Vikas | Vikas |
| Last Name | Kumar Yadav | Kumar Yadav | Kumar Yadav |
| Gender | Male | Male | Male |
| Date of Birth | 1976-11-24 | 1976-11-24 | 1976-11-24 |
| Mobile No. | 9810075469 | +919810075469 | 919810075469 |
| Email | rhlsaxena7@gmail.com | rhlsaxena7@gmail.com | rhlsaxena7@gmail.com |
| Email Verified | true | | |
| Mobile Verified | true | | |

Customer Profile Details section (editable fields with pencil icons):
- CP First Name: Vikas Vikram
- CP Last Name: Kumar Yadav
- CP DOB: 24/11/1976
- CP Gender: Male
- Type of Changes: First Name
- No of Changes: 1
- Expert Status: Accept
- Email Body: Name Change Request

**Screen reference — My Profile - Basic Details (Name / Gender / DOB):**

Screenshot of the IndiGo website member "My Profile" page (member logged in as Shivangi Singh, IndiGo BluChips Balance 50,000). Top navigation: Book, Trips, Deals and Offers, Check-in, IndiGo BluChip.

The "Basic Details" card shows the editable profile fields the agent guides the member to update:

1. Helper text: "Name should be as per govt ID".
2. Gender selector with radio buttons: Male / Female (Female selected), with a pencil (edit) icon next to it to change gender.
3. First name field: "Shivangi".
4. Last name field: "Singh".
5. Date of birth field: "02-11-1998" with a pencil (edit) icon to edit it.
6. Helper text: "* Enter date of birth in (DD-MM-YYYY) format".

Agent action: direct the member to this My Profile > Basic Details screen to self-update name, gender, or date of birth; click the pencil/edit icon next to the relevant field and ensure the name matches the government ID and DOB is in DD-MM-YYYY format.

## 1. NA

*Scenario:* Name1 | Backend migration (before enrolment date before 1-Oct-24) or new enrolment

## 2. Name1

*Scenario:* Name 2 | During Account activation stage or Member put into enrolment flow or backend change done by Prog. Ops/Salesforce

## 3. Name 2

*Scenario:* Name 3 | Backend change done by Prog. Ops/Salesforce (if not done in previous step). If done in previous step, deny the request

**Screen reference — Compare Profile Details - Submit for Approval dialog:**

UI screenshot: "Compare Profile Details" screen with a "Submit for Approval" confirmation dialog.

Background screen ("Compare Profile Details"):
1. Shows side-by-side profile data columns across systems, including "Navitaire" and "Capillary" (a third column is partially visible on the left).
2. Each column lists fields such as Api Status (Success), name (e.g. "...ar Yadav"), a date (e.g. 11-24), a number (e.g. 10075469), Email (rhlsaxena7@gmail.com), and boolean flags (true).

Foreground dialog ("Submit for Approval"):
1. Title: "Submit for Approval".
2. Prompt text: "Are you sure to submit for approval?"
3. A checkbox on the left (highlighted) that the agent must tick to confirm.
4. Buttons at bottom right: "Cancel" and "Save".

Agent action: After reviewing the compared profile details, tick the confirmation checkbox and click "Save" to submit the profile for approval (or "Cancel" to abort).

## 4. Name 3

*Scenario:* Name 4 | Deny the request

**SOP — steps:**
Greet member.  Request member to share his/her concern.  As per the member’s request they want to update the name on the IBC account we need to ask the member to share Govt ID proof (Passport/Aadhar card). Follow below steps for the same-  Verify Source of request o Ensure the email is received from the registered email ID associated with the member’s account along with Name format and member’s consent.  Check for previous Name changes o 	Go to Audit Log in LMS and look for any name change activity o 	Look for any previous name change activity: If a name change has already been processed by Carrier Name: Program  Ops or Salesforce, deny the request and respond as per the denial email template, otherwise raise for profile update.   Any new name change request, where total count of name update done from account creation date is more than 3, deny the request, otherwise raise for profile update.    If previous name changes done in IBC account of any member due to CC error/6E error, mention the same in remarks column while raising for name change approval on utility.  Compare the requested name update with the government ID proof provided by the member. If requested name doesn’t match with government ID shared, then deny the request and share denial email per SOP. If name matches the govt. id shared, then follow below steps to raise request via Salesforce.   Steps to raise request on Salesforce
 | 7.c Check for compare details on all platforms for the fetched mobile number    7.d Click on the pencil icon under member profile details – Update the name as per request>Enter the FFN manually>Enter “Remarks”>Click on “Save”    7.e Attach the govt. if proof on the case. Click on “Related” >>> Scroll down for “Files” >>> Click on “Add Files”>>> Click on “Related files” >>> Choose the support docs >>> Click on “Add”. | 
 | 7.f Click on “Drop down” and then click on “Submit approval”    7.g Click on “Check Box” and then click on “Save” | 
 |  | Refresh the    versa then this needs to
 | 8.  Tech Error Troubleshooting and resolution in Customer profile utility on SF: 8a. Compare Profile Details is not fetching Step1:  First we need to check that member has raised his/her concern from registered email ID and if not then ask member to share concern from the registered email ID. Step2:  We will check registered contact number of the member in the capillary to validate whether the profile is getting fetched with registered mobile number or not in salesforce in case of no data found.     Step3-  If profile details is not getting fetched with registered mobile number then we will edit the registered mobile number in Loyalty CIAM fields manually.  Case Open >>Details >> Scroll down to Loyalty CIAM fields >> Update country code and Loyalty mobile number >> page – ctrl + shift + R        If we have the same mobile number in CIAM and Navitaire but different in Capillary or vicebe raised with program ops to make all details same in CIAM, Navitaire and Capillary as member’s registered email address and contact should be same. | Refresh the    versa then this needs to

## 2b. DOB/Gender update request

*Scenario:* Member entered incorrect DOB while registering & now requesting to update the correct date of birth.  → Member by mistake added incorrect gender/DOB and wants to update

**SOP — steps:**
Greet member.  Request member to share his/her concern.  As per the member’s concern they are requesting for DOB/Gender update on the IBC account- We will ask the member to login to IBC account > Click on My profile option> Under personal details there will be a pencil icon next to DOB and the member can then edit the DOB/Gender.       If member has already changed the DOB once via website or the pencil icon is not visible to the member then Take request from member with government id & follow the “profile update process” to update DOB. (Refer Maker process 2a for steps and screenshot)

## 2c. Email ID update request

*Scenario:* Member for any reason wants to update his email ID in account

**SOP — steps:**
Greet & verify member  Request member to share his/her concern.  Probe the member about the reason for email change – e.g. Lost access to email id, email id hacked, email storage is full.  We need to check on LMS that the new email address provided by member is linked to any account or not, if yes then we will suggest the member that there is an account already exist and to use the account.   If no account found then we will request the member to write from the registered email id for email id change request, in case member don’t have access to the registered email id then we will call on the registered mobile no and do the verification to ensure that request has come from the verified member( Ask member FFN no , registered email id , DOB , name on IBC account for DPA).  Once verification is done, we will raise the request to Program OPS by attaching the consent received from registered email id or snap of the call done on mobile no for consent and ask member to wait for 24- 48 hrs  Post validation from Program Ops team, they will put the member in activation flow (In activation flow member will be able to change email id without having to change the profile name). Refer to Enrolment & login for activation flow & Flag  Post member is put-in activation flow the request member- Go to 6ewebsite>>> Login via Registered mobile no >>> Enter OTP >>> Update the email ID (Member can update DOB as well) >> Complete OTP verification on mobile no & email id >>> Create Password >>> Login again.    Note: Check from activity logs if email change done previously, if yes then highlight this to Program Ops while raising for email id change request.

## 2d. Mobile no update request

*Scenario:* Member for any reason wants to update his mobile number in account

**SOP — steps:**
Greet & verify member  Request member to share his/her concern.  Probe the member about the reason for mobile no change by out calling and inform that mobile no. change is not possible in IBC account due to system limitation.   Offer alternative solution- o Member can make a new IBC account with new mobile no. & new email ID using same name & DOB. (Note – Inform member if he creates a new account with new email ID & new mobile no., overall process will become faster as only account merging will be required in that case)    Once new account is made, new & old IBC account can be merged.   If member does not agree to create an IBC with a new email ID, then inform member that the email ID registered with old account needs to be released & follow below steps:  Send an email to member asking for consent to release existing email ID from existing IBC account.  o After receiving member’s consent, send email to Prog. Ops to free existing email ID from IBC account. o After Prog. Ops confirmation, call & request member to create a new account with new mobile no. & old email ID.  Request member to create new account over the phone call itself. If member not reachable, send an email.  o Once new account created, take details from member & send to prog. Ops for merging the IBC account.   Once accounts are merged, inform member about the same.

## 2e. Nominee details change request

*Scenario:* Member by mistake added duplicate nominee, incorrect details of nominee added like DOB, typo error in name.

Nominee addition/update Policy  “Nominee” means any person who has been nominated by the Member and is a minimum of 2 (Two) years of age at the time of enrollment as a Nominee, and those who can enjoy the benefits of the  Program as per the Terms and Conditions o A Member can add up to 5 (Five) Nominees by logging into their IndiGo BluChip Account from the  IndiGo website or through the IndiGo Mobile App o A Member may change/delete a Nominee after 1 (One) year from the date of addition by logging into their IndiGo BluChip Account on the IndiGo Website or the IndiGo Mobile App.  Once added, a Nominee cannot be changed for one year from the date the record was added. In case of Typo error , shortened name , legal name change we can raise to internal team for correction, however complete body swap not allowed  A Member cannot earn IndiGo BluChips for any Accrual Activity done by a Nominee. Earning of IndiGo  BluChips is only for Member’s own Accrual Activities
**SOP — steps:**
Greet member.  Request member to share his/her concern and ask FFN no  As per the member’s concern they want to update/change the nominee details. E.g. Nominee name on account is incorrect, has typo error and wants to correct the same, complete name change of nominee.  If member requests for complete name change of nominee, then inform that complete name change is not possible and they can remove the nominee with incorrect name after 365 days  In case of any typo error, spelling mistake, duplicate nominee we will ask the member to share government id proof of the nominee and raise to program ops for correction    Note: - Advise the member that nominees need to be above 2 years and up to 5 nominees can be added. Also, once a nominee is added they can only be removed post 365 days.

## 2f. How to add Nominee

*Scenario:* Member called to know the process of how to add nominee

**SOP — steps:**
Greet member.  Request member to share his/her concern.  Advise the member that nominees need to be above 2 years and upto 5 nominees can be added. Also, once a nominee is added they can only be removed post 365 days.  For nominee addition we will guide the member to add via IndiGo website/app & follow below steps
Flow for updating nominee on 6E-
1: Click on My Nominees option in logged-in website/app
Member will be able to view the nominee if added any.
Click on “Add Nominee” option, Enter Gender, Name, DOB of the nominee and click on “Save” Option

**Screen reference — Add upto five nominees - Nominee management screen:**

UI screenshot of the IndiGo BluChip nominee management page.

What the screen shows:
1. Header: "Add upto five nominees" with a note "Nominee once added cannot be removed for 365 days".
2. A "BACK TO HOME PAGE" link at the top left.
3. A list of currently added nominees, each in an expandable row (chevron to expand):
   - Shanvi Pathak — Female | 12 Years
   - Senior Citizen — Male | 65 Years
   - Child Child — Female | 3 Years
4. An "+ ADD NOMINEE" link on the right side below the list.
5. A "Remove Nominee" button centered at the bottom.

What the agent should do:
- To add a nominee, click "+ ADD NOMINEE" (up to five nominees can be added).
- To remove a nominee, click "Remove Nominee" (note: a nominee cannot be removed for 365 days after being added).
- Click the chevron on any nominee row to expand and view/edit that nominee's details.

**Screen reference — Add upto 5 Nominees screen:**

UI screenshot of the IndiGo BluChip Nominee management screen.

What the screen shows:
1. Header "Add upto 5 Nominees" with a note: "Nominee once added cannot be removed for 365 days".
2. A "< BACK TO HOME PAGE" link at top left to return to the home page.
3. A list of existing nominees, each on its own expandable row (chevron to expand details):
   - "IBC Test Nominee" — Female | 79 Years
   - "Test Minor" — Male | 11 Years
   - "Infant Infant" — Male | 3 Years
4. A "+ ADD NOMINEE" link on the right to add a new nominee (up to 5 total).
5. A "Remove Nominee" button at the bottom center.

Agent actions:
- To add a nominee, click "+ ADD NOMINEE".
- To remove a nominee, click the "Remove Nominee" button (note: a nominee cannot be removed within 365 days of being added).
- Use the chevron on each nominee row to expand and view that nominee's details.

**Screen reference — Nominee Details Screen - Add / Edit Nominee:**

IndiGo loyalty portal nominee management screen (used to add or edit a nominee).

What the screen shows and what the agent should do:

1. Top-left shows the IndiGo logo; top-right has a profile dropdown toggle.
2. A list of existing nominees is shown as expandable rows:
   - "Infant Infant" — Male | 3 Years (collapsed, with a chevron to expand).
   - "Mohan sharma" — Male | 27 Years (selected/expanded row, highlighted in blue).
3. The expanded nominee shows editable fields:
   - Gender selector: radio buttons "Male" (selected) / "Female".
   - Note: "Name should be as per government ID".
   - First name field: "Mohan".
   - Last name field: "sharma".
   - Date of birth field: "01-08-1998".
   - Helper text: "*Please enter date of birth in (DD-MM-YYYY) format i.e. 25-04-1998".
4. Action links/buttons:
   - "+ ADD NOMINEE" link (top-right of the form area) — click to add a new nominee.
   - "Remove Nominee" button — click to delete the selected nominee.
   - "Save" button (bottom-right) — click to save the nominee details.

To add a nominee: click "+ ADD NOMINEE", select gender, enter first name, last name (as per government ID) and date of birth in DD-MM-YYYY format, then click "Save".

## 3. Merge Membership accounts

## 3. Member has 2 IBC accounts

*Scenario:* Member has two accounts and wants to initiate a merger.  → User has two different accounts under two different mail ids/phone numbers  → An already existing member is enrolled into the loyalty program by purchasing a credit card by providing a new mobile number and email id

**SOP — steps:**
Greet & verify member  Request member to share his/her concern.  Take details of both the accounts to be merged & understand the reason why he/she wants to merge the accounts.  Check from account merger guidelines whether it is allowed to merge the accounts or not for this by reviewing the details provided by him/her. (In case IBC account linked with co-brand card will be treated as Primary account for merge) 5a. If accounts can be merged as per policy, Do Mandatory DPA by calling the mobile number registered with the secondary account and confirm the member’s consent for account merger then ask the member to share the consent form registered email id of both accounts and request member to mention the details of Primary & secondary account  5b. If account cannot be merged as per policy, then politely inform members with the reason why account cannot be merged.  Send email to program Ops team with a request for account merger along with the details of both the accounts that need to be merged along with consent received from both email id’s registered on the IBC account  Once program ops team has responded by informing the merger of account, do validation at your end & inform the member on email ID of both the merged accounts.  Closing Statement    Account Merger Guidelines  Allowed  Name & DOB matches but contact details are different  Minor Name mismatches but name initials & DOB match  -Secondary account that needs to be merged must have some IBC balance/benefits. In case of no IBC balance/benefits in secondary account, we will inform member that there is no need to merge the accounts. If member wants to delete the secondary account, then we can take the request for deletion.  Note- Primary account may have 0 benefits/0 IBC balance and we can take the request for merging accounts  -Check status of primary & secondary account it should be "verified". In case status of any account is Locked or UI (Under investigation) then raise this to Program ops, and they will give confirmation on the merge  -Check if any cobrand card is linked with Primary or secondary account-  o If with Primary account, then send it to Prog Ops for merging the accounts.  o If the cobrand card is linked with secondary account, then request member to make this account as Primary and in case member denies, then inform member that account merge will not be possible.    Not Allowed  Family account merger or accounts with persons having different identities not allowed  DOB mismatch & Name mismatch between the two accounts  -If any co-brand is linked with secondary IBC account, then merge is not allowed, we will advise member that IBC account linked with co-brand card will be treated as Primary account for merge
Transfer of Membership

## 4. Transfer to legal heir due to death of  Member

*Scenario:* In case of demise if immediate family member contacts us for transfer of privileges and benefits

**SOP — steps:**
Greet & verify member  Request member to share his/her concern.  Empathize the member for their loss and explain the process of Membership account transfer.  Ask the legal heir to share the required documents for the transfer request and follow the verification process to ensure that legal heir’s claim is validated (Legal heir to share Government issued Death Certificate, Membership ID or registered email ID of the deceased Member, Membership ID of the legal heir (as applicable) and relationship proof of legal heir with the deceased  Member)  Request member to share the email consent from the email id deceased member’s / call on registered mobile no. to verify the request is genuine. In case member doesn’t have access to the email/id mobile no of deceased then raise to Program ops with the findings & resolution on the further steps.  If member is able to share consent from registered emailed/Mobile no of deceased member’s IBC account, raise request to program Ops with all details and advise member to wait.  Important Note: -  Before processing an account transfer request, the legal heir’s claim must be verified and validated.  The legal heir may be asked to provide confirmation from the registered email address associated with the deceased member’s account or consent obtained through an outbound call to the registered mobile number  If the legal heir does not have access to the registered email or mobile number, a Data Privacy Authentication (DPA) must be completed by the legal heir using details from the deceased member’s account (e.g., Date of Birth, Name, Registered Email, and Mobile Number).  Only the IndiGo BluChips accumulated as of the date of demise of a member will be transferred to/redeemed by his/her legal heir. All Tier Benefits, vouchers, or any other benefits associated with the IndiGo BluChip Account of the deceased Member will stand forfeited.  In case of multiple legal heirs, IndiGo BluChips will be transferred to the legal heir's IndiGo BluChip Account whose request for transfer is first received by IndiGo at the IndiGo member care email ID, subject always to receipt of documents satisfactory to IndiGo.
Account Info Issue

## 5a. Tech error - Incorrect Gender Reflecting in profile

*Scenario:* Member's Gender is reflecting incorrect in the Profile section on IBC account

**SOP — steps:**
Greet member.  Request member to share his/her concern and ask FFN from member.  Retrieve FFN on LMS portal and check the gender.  If correct gender is reflecting in IBC account of member then fetch profile on salesforce and compare the gender on all 3 platform (Navitaire, Capillary, CIAM), in case gender is showing different on any 3 platform then this may be the reason for gender mismatch on Profile section at member’s end .Follow the profile update process and get the gender updated.  If incorrect gender reflecting on member’s IBC account, then we will ask the member to login to IBC account > Click on My profile option> Under personal details there will be a pencil icon next to gender and the member can then edit the Gender. If pencil ICON is not visible, then follow the profile update process.       If member has already changed the Gender once via website or the pencil icon is not visible to the member then Take written request from member with valid reasons & government id. Post validation follow the makes process to update DOB. (Refer Name update request for steps and screenshot)

## 5b. DOB Mismatch by 1 day

*Scenario:* Member's DOB is reflecting incorrect (Mismatch by 1 day) in the Profile section on  IBC account

**SOP — steps:**
Greet & verify member  Request member to share concern.   Check the DOB on CIAM utility portal, due to a tech issue the name might show incorrect by 1 day  As per the member’s concern they are requesting for DOB update on the IBC account- We will ask the member to login to IBC account > Click on My profile option> Under personal details there will be a pencil icon next to DOB and the member can then edit the DOB.  In case, the pencil icon is not visible under My profile on website/app or the details under CIAM still shows incorrect then take government id proof from the member and follow the profile utility update process to update the correct DOB.  Advise member to wait for 24-48 hrs and once DOB is correct, outcall the member to inform.

## 5c. Member Name Conflict – Dashboard vs LMS

*Scenario:* As per member, the name on IBC account is reflecting incorrect  , not matching with First/Last name

**SOP — steps:**

**Screen reference — Compare Profile Details across CIAM, Navitaire, and Capillary:**

UI screenshot: Salesforce record "Details" tab showing a side-by-side "Compare Profile Details" view for a member (FFN masked, ending 098). Used to spot mismatches in member data across the three source systems (CIAM, Navitaire, Capillary).

Agent actions / what the screen shows:
1. Open the member record and select the "Details" tab (tabs shown: Feed | Details | Related).
2. Locate the highlighted header "Compare Profile Details for 90...098" (the member's FFN).
3. Review the three columns side by side and compare each field for discrepancies:

| Field | CIAM | Navitaire | Capillary |
|---|---|---|---|
| Api Status | Success | Success | Success |
| First Name | Aparna | Aparna | Aparna |
| Last Name | Bhattacharya | Bhattacharya | Bhattacharya |
| Gender | Female | Female | Female |
| Date of Birth | 1977-01-10 | 1977-01-10 | 1977-01-10 |
| Mobile No. | (masked ...98) | +91...7098 | 9190...98 |
| Email | shy...jee109@gmail.com | shy...nerjee109@gmail.com | shy...anerjee109@gmail.com |
| Email Verified | true | — | — |
| Mobile Verified | true | — | — |
| Country Code | +91 | — | — |
| Status | — | — | Verified |
| Activation Date | — | — | 2024-12-05T23:56:58+05:30 |

4. Compare First Name / Last Name / Gender / Date of Birth / Email / Mobile No. across all three systems to confirm whether values match or conflict.
5. Expand the "Customer Profile Details" section at the bottom for additional details if needed.

**Screen reference — Compare Profile Details for 55213071:**

UI screenshot: "Compare Profile Details for 55213071" screen. This tool displays a member's profile fields side-by-side across three systems so the agent can spot mismatches.

1. The screen header reads "Compare Profile Details for [FFN/Member ID]" (here 55213071).
2. Three columns are shown, one per source system: CIAM, Navitaire, and Capillary.
3. CIAM column lists fields: Api Status, First Name, Last Name, Gender, Date of Birth, Mobile No., Email, Email Verified, Mobile Verified, Country Code.
4. Navitaire column lists fields: Api Status, First Name, Last Name, Gender, Date of Birth, Mobile No., Email.
5. Capillary column lists fields: Api Status, First Name, Last Name, Gender, Date of Birth, Mobile No., Email, Status, Activation Date.
6. In this example the "Api Status" value for all three systems shows "Data Not Found" and the remaining field values are blank.

Agent action: Use this comparison view to check whether profile details (Name, Gender, DOB, etc.) match across CIAM, Navitaire, and Capillary and to identify any discrepancy between the dashboard/LMS and the underlying systems.

**Screen reference — Compare Profile Details for 7977173011 (CIAM / Navitaire / Capillary):**

## Compare Profile Details for 7977173011

This screen is an internal agent diagnostic tool that pulls and compares a member's profile details side-by-side across three source systems: **CIAM**, **Navitaire**, and **Capillary**. The agent uses it to identify where a member's details mismatch between systems (e.g., name/DOB/gender conflict between dashboard and LMS).

Side-by-side comparison shown for member 7977173011:

| Field | CIAM | Navitaire | Capillary |
|---|---|---|---|
| Api Status | Success | Success | Success |
| First Name | Ravi | Ravi | SIMRAN |
| Last Name | Bhatia | Bhatia | Bhatia |
| Gender | N-A | Other | Female |
| Date of Birth | 1964-10-07 | 1964-10-07 | 1967-04-17 |
| Mobile No. | +917977173011 | 7977173011 | 917977173011 |
| Email | 917977173011@goindigo.in | bhatiasrav@gmail.com | ravsim64@gmail.com |
| Email Verified | false | — | — |
| Mobile Verified | false | — | — |
| Country Code | +91 | — | — |
| Status | — | — | Verified |
| Activation Date | — | — | 2025-01-02T12:47:56+05:30 |

What the agent should do:
1. Read across the three columns (CIAM, Navitaire, Capillary) to spot mismatched fields.
2. Note the conflict: First Name, Gender, Date of Birth and Email differ in the Capillary record (SIMRAN / Female / 1967-04-17) versus the matching CIAM and Navitaire records (Ravi / 1964-10-07).
3. Use these flagged discrepancies to drive the correction/escalation per the relevant profile-mismatch scenario.

**Screen reference — Compare Profile Details for 9823240552:**

UI screenshot: "Compare Profile Details for 9823240552" — a side-by-side comparison of a member's profile across three systems (CIAM, Navitaire, Capillary). The agent uses this view to check whether profile fields match across systems when diagnosing a mismatch.

What the screen shows (three columns):

**CIAM**
| Field | Value |
|---|---|
| Api Status | Success |
| First Name | RYAN ROQUE |
| Last Name | RODRIGUES |
| Gender | Male |
| Date of Birth | 1976-11-29 |
| Mobile No. | +919823240552 |
| Email | ryanshorn@gmail.com |
| Email Verified | true |
| Mobile Verified | false |
| Country Code | +91 |

**Navitaire**
| Field | Value |
|---|---|
| Api Status | Success |
| First Name | RYAN ROQUE |
| Last Name | RODRIGUES |
| Gender | Male |
| Date of Birth | 1976-11-29 |
| Mobile No. | 9823240552 |
| Email | ryanshorn@gmail.com |

**Capillary**
| Field | Value |
|---|---|
| Api Status | Success |
| First Name | RYAN ROQUE |
| Last Name | RODRIGUES |
| Gender | Male |
| Date of Birth | 1976-11-29 |
| Mobile No. | 919823240552 |
| Email | ryanshorn@gmail.com |
| Status | Verified |
| Activation Date | 2024-09-20T21:59:25+05:30 |

Agent action: Compare the field values across the three columns (CIAM, Navitaire, Capillary) to identify any mismatch (e.g., name, DOB, gender) between the dashboard/CIAM and the LMS systems.

## 5d. Tech Error - Loyalty Profile info/dashboard not visible

*Scenario:* As per member while member login to IBC account they are unable to see the Dashboard option/Loyalty Profile info (e.g. FFN no, tier details)

**SOP — steps:**
Greet & verify member  Request member to share concern, check if member is logged in and guide how to check details, in case member is still unable to view the details then do basic troubleshooting o 	Advise members to Clear cache & cookies then try to login, ask member to login using another browser or ask them to log-out and login again to see it details are visible  3.In case even after basic troubleshooting if the profile details/dashboard is not visible then advise member to share the screenshot and raise to program ops.  4. Advise the member to wait for 24- 48 hrs and once resolution received from program ops, outcall the member and ask them to login and verify if details are visible

**Screen reference — IndiGo BluChip Tier Benefits Dashboard:**

This is a screenshot of the IndiGo BluChip member dashboard (loyalty profile) on the IndiGo website, showing where tier benefits and BluChips balance are displayed.

What the screen shows:
1. Top navigation bar with menu items: Book, Trips, Deals and Offers, Check-in, IndiGo BluChip.
2. Top-right shows the member's "IndiGo BluChips Balance 19,253" and a profile/account icon ("A").
3. Two tabs below the nav bar: "Tier Benefit" (currently selected) and "Partnerships".
4. Heading: "WHAT YOUR INDIGO BLUCHIP BLU 2 MEMBERSHIP CAN DO?" with subheading "Your Tier Benefits".
5. A benefit card displaying a BluChip "Made in IndiGo" coin graphic, a badge reading "76 Passes Left", and benefit text "20 6E Prime passes".
6. A "VIEW CLAIMED BENEFITS" link below the benefit card.

Agent action: To check a member's tier (here BLU 2), BluChips balance, and tier benefits, view the IndiGo BluChip dashboard. Select the "Tier Benefit" tab to see available benefits and click "VIEW CLAIMED BENEFITS" to review benefits already used.

## 6. Travel Document Discrepancy

## 6a. Incorrect/missing loyalty details on boarding pass

*Scenario:* As per the member the loyalty detail e.g. FFN no, tier details are not reflecting of reflecting as incorrect on  the boarding pass

**SOP — steps:**
Greet & verify member  Request member to share concern. Check with member if the loyalty details are missing or showing incorrect o 	In case FFN is missing on Boarding pass –   If FFN is linked with PNR, then advise the member to undo check-in and check-in again and the new boarding pass will have FFN updated.   In case FFN is not linked with PNR, then add member’s FFN on PNR and ask member to undo check-in and check-in again and the new boarding pass will have FFN updated.  In case FFN is incorrect on the Boarding pass- Identify how incorrect FFN got added. If it is added from web/app then retrieve the added FFN of PNR on LMS and check with member if he/she can identify the mobile no. /email id.   If member is able to identify the details, advise member for merge of both IBC accounts accordingly if eligible for merging the accounts as per merge policy  If member is unable to identify the details, then share your observation with prog. Ops along with the source of the agent who added FFN on PNR for next steps and ask member to wait.  In case incorrect tier details is reflecting on boarding pass- Go to sky speed>>> Do ctrl+f5>>> Retrieve by mobile no/email id >>> Under Member programs click on "Add/edit" and update the correct tier as per LMS. Then ask member to undo check-in and then check-in again for updated boarding pass

## Boarding Pass Design-Counter

## Boarding Pass Generated at - Kiosk

## Web Boarding Pass

**Reference — IndiGo Boarding Pass - Sample (Loyalty Tier & FFN shown):**

Sample IndiGo boarding pass showing where loyalty details (Tier and FFN) appear.

**Main boarding pass:**
- Passenger: SUBRAMANIAN/KRISHNAM/MR
- From: MUMBAI — To: CHHATRAPATI SAMBHAJI NAGAR
- Flight: TK 6780 (Also 6E 1706)
- Gate: A 21
- Boarding Zone: A
- Seat: 19 C
- Boarding: 1400 Hrs
- Tier: BLU3
- FFN: 983451212
- Date: 25 Mar 2019
- Departure: 1445 Hrs
- Services: DFNS, INFT, VGML, WCHR
- Seq: 0035
- E-TKT#: 32145678910214
- Note: Gate is subject to change and will close 25 minutes prior to departure.

**Stub (right side):**
- SUBRAMANIAN/KRISH
- BOM To IXU
- Flight: TK 6780
- Date: 25 Mar 2019
- PNR: W88PYL
- Services: DFNS, INFT, VGML, WCHR
- Seat: 19 C
- Seq: 021

**Screen reference — Boarding Pass (Self Check-In) showing Tier and FFN loyalty details:**

Image: IndiGo Boarding Pass (Self Check-In) — a sample boarding pass illustrating where loyalty (BluChip) details appear, used to verify incorrect/missing loyalty details on a boarding pass.

What the boarding pass shows:
1. Header: "Boarding Pass (Self Check-In)" with the IndiGo logo.
2. Passenger name: SUBRAMANIAN/KRISHNAM/MR (right stub: SUBRAMANIAN/KRISH/M).
3. Route: MUMBAI To CHHATRAPATI SAMBHAJI NAGAR (right stub: BOM To IXU).
4. Flight: TK 6780 (Also 6E 1706).
5. Gate: A 21; Boarding Zone: A; Seat: 19 C; Boarding: 1400 Hrs.
6. Date: 25 Mar 2019; Departure: 1445 Hrs; Seq: 0035.
7. Loyalty details line: Tier: BLU3   FFN: 983451212.
8. Services: DFNS, INFT, VGML, WCHR.
9. E-TKT#: 32145678910214; PNR (right stub): W88PYL.
10. Note: "Gate is subject to change and will close 25 minutes prior to departure."

Agent action: Verify the Tier and FFN (Frequent Flyer Number / IBC membership number) fields on the boarding pass against the member's profile to confirm/correct incorrect or missing loyalty details.

**Reference — Boarding Pass (Web Check-In) — Loyalty Tier & FFN:**

Sample IndiGo Boarding Pass (Web Check-In) showing where loyalty details (Tier and FFN) appear. Used as reference for scenario 6a (incorrect/missing loyalty details on boarding pass).

**Main boarding pass:**
- Header: IndiGo — Boarding Pass (Web Check-In)
- Passenger: SUBRAMANIAN/KRISH MR
- Route: CHHATRAPATI SAMBHAJI NAGAR To THIRUVANANTHAPURAM
- Flight: 6E 7634
- Gate: -
- Boarding Time: 1245 Hrs
- Boarding: Zone 1
- Seat: 28 F
- Date: 25 Mar 2019
- Seq: 0001
- Departure: 1445
- Services: FFWD
- **Tier: BLU3**
- **FFN: 983451212**
- Note: "Gate is subject to change and will close 25 minutes prior to departure"

**Tear-off stub (right side):**
- Passenger: SUBRAMANIAN/KRISH MR
- Route: CHHATRAPATI SAMBHAJI NAGAR To THIRUVANANTHAPURAM
- PNR: W88PYL
- Flight: 6E 7634
- Date: 25 Mar 2019
- Services: FFWD
- Seat: 19C
- Seq: 0001

## 6b. Incorrect/missing loyalty details on Ticket itinerary

*Scenario:* As the member the loyalty detail e.g. FFN no, tier details are not    reflecting of reflecting as incorrect on the Ticket itinerary

**SOP — steps:**
Greet member.  Request member to share his/her concern. Check with member if the loyalty details are missing or showing incorrect o In case FFN is missing on Itinerary – Check if FFN is linked with PNR, if yes then ask member to correct FFN is on CIAM or missing, if yes then raise to program ops else ask member to reprint the itinerary again  In case FFN is incorrect on the Itinerary- - Identify how incorrect FFN got added. If it is added from web/app, then retrieve the added FFN of PNR on LMS and check with member   If he/she can identify the mobile no./email id, then advise member for merger of both IBC accounts accordingly if eligible for merging the accounts as per merge policy   If member unable to identify share the details with your observation with prog. Ops along with the source of the agent who added FFN on PNR for next steps and ask member to wait.  In case incorrect tier details is reflecting on itinerary- Go to sky speed Do ctrl+f5>retrieve by mobile no/email id >Under Member programs click on "Add/edit" and update the correct tier as per LMS. Then ask member to reprint the itinerary again and details will be updated either we can also share the E-ticket with the member via Skyspeed (Fetch Pnr on Skyspeed >>> Click F8>>> Send Itinerary via Email >> Enter email >> Click on Next

**Screen reference — End Record screen - Send Itinerary via Email:**

UI screenshot of an airline reservation/PNR system ("End Record" screen) for PNR QUNG2T (Booking: Confirmed, Payment: Complete, Total Cost: 2,948.00 INR).

Actionable steps highlighted on screen:

1. Under "Action to perform", the "End Record" radio option is selected (other options: End Record and Clear, Ignore Changes (Ctrl+10), Ignore Changes and Clear).
2. In the "Itinerary details" section, set the "Send Itinerary via" dropdown (highlighted) to the desired delivery method (e.g., Email).
3. Confirm the recipient details: Contact Name "1. Mishra, Alok" and enter/verify the "Email Address" field (highlighted) — e.g., ALOK.MISHRA@GOINDIGO.IN.
4. Left sidebar provides reference panels: Flight Information, Other Services, Passengers (1), Contact Information (1), Payments, Comments.
5. Click the "Next" button (highlighted, bottom right) to proceed and send the itinerary. ("Cancel" and "Back" buttons are also available.)

**Screen reference — Ticket Itinerary / Booking Confirmation:**

This is a screenshot of an IndiGo Ticket Itinerary / Booking Confirmation. The agent uses this view to verify loyalty (IBC/FFN) details and booking information on a member's itinerary (scenario 6b).

Key elements shown:
1. Header: Date 29/03/2024, 13:00; "Modify Itinerary" link; IndiGo logo. Note: "*Date of booking 29th March 2024 9:19".
2. PNR / Booking Ref.: WKNPHZ — Status: Confirmed; Payment Status: Complete.
3. Passenger Information:
   - John Doe — Adult | Male | 25 year | FF No. 123456789
   - Sector: DEL-BOM | Seat: 30E (Middle)
   - 6E Add-ons: Fast Forward, Travel Assistance, Baggage Protection
4. Departing Flight: 6E624, A320 — Check-in/Bag Drop Closes: 16:25 hrs
   - Delhi (DEL): Indira Gandhi Intl. Airport [T1], 13:05, 30 Oct 2024
   - Mumbai (BOM): Chhatrapati Shivaji Intl. Airport [T1], Travel Time 8 hour 30 min, 14:05, 30 Oct 2024
   - Note: "*Booking date reflects in UTC (Coordinated Universal Time), all other timings mentioned are as per local time"
5. Baggage Information table:
   - S.No 1 | Sector DEL-BOM | Adult Check-in 15 KG, Cabin Up to 7kg
   - Note: "Check-in Cabin: One hand bag up to 7 KG and 115 CM (L+W+H), shall be allowed per customer. For contactless travel we encourage you to place it under the seat in front, on board."

Agent action: Use this itinerary to confirm whether the member's loyalty/FF number (FF No. 123456789) is correctly captured on the booking; if incorrect or missing, follow scenario 6b resolution steps.

## 6c. Incorrect/missing details in IBC account statement

*Scenario:* As per the member Details - FFN no, Tier & IBC balance is reflecting incorrect or missing on the account state- ment

**SOP — steps:**
Greet member.  Request member to share his/her concern and the account statement. Validate by checking the account statement if the member is referring to the correct statement    In case IndiGo BluChips balance is missing/incorrect on the account balance- Check on LMS if any applicable amount was accrued for the account statement of the month member is referring to.   If no accrual was applicable, then assist the member and explain that correct IBC is reflecting in the account statement  In case the IBC balance is incorrect and as per LMS the IBC’s accrued is not matching then raise to program ops for resolution and advise member to wait 24-48 hrs.   In case of incorrect IBC balance reflecting on account statement check if the statement sent to the member release date and advise member that monthly statement is basis last month earning and current month earning will reflect in next month statement  In case FFN no is reflecting incorrectly on the account statement- Check the FFN on CIAM utility, if the FFN under CIAM tab is not matching as under LMS tab and email id and mobile number is matching then raise to program ops  In case Name is reflecting incorrectly on the account statement – Check the FFN on LMS   If name is correct in IBC account and matching with name on CIAM & Navitaire then raise with Program Ops with the account statement shared by member  If name on LMS doesn’t match with CIAM of Navitaire then follow the name update process  In case Tier details is missing or incorrect on the monthly account statement, check the tier details on all 3 portals and for any discrepancy raise to Program OPS

## 6d. Monthly Account Statement not received

*Scenario:* As per the member IBC account monthly statement has not been received

**SOP — steps:**
Greet member.  Request member to share his/her concern.  Ask for FFN and check the status of account in LMS, status should be “Verified” on LMS.  Advise member to check if account statement is received in registered email id, possibly member might be checking account statement on incorrect email id. Also advise member to check spam folder or mail storage if it is not full.  4. As per the member they have not received the monthly statement. Probe with the member if they for which month the account statement is not received. IBC account statement is released for previous month on 5th of the current month.  o 	In case the monthly account statement is not received then check with 6E spoc if monthly account statement is deployed or not. If not deployed, then advise the member to wait. In case the account statement is deployed and member has not received, then raise request to program ops for the same.

## 7. Policy and information dispute

## 7a. Member disputing T&C

*Scenario:* As per the member they are disputing with tnc as mentioned on the website

**SOP — steps:**
Greet member.  Request member to share his/her concern.  Probe the member regarding the tnc for which they are disputing, try to understand the reason for dispute and refer to tnc to validate if the reason for dispute in correct.   If the reason is correct then consult with TL and post TL’s alignment, highlight to internal IBC team for validation and advice member to wait for 24-48 hrs  If the dispute reason is not valid then give denial as per SOP, if the member is escalating then follow the escalation matrix

## Link to check for IndiGo BluChip tnc- Terms and Conditions

## 7b. Member disputing FAQs/website info.

*Scenario:* As per the member they are not aligned with the FAQ's/website info and are raising dispute on the same

**SOP — steps:**
Greet member.  Request member to share his/her concern.  Probe the member regarding the FAQ’s/info for which they are disputing, try to understand the reason for dispute and refer to tnc to validate if the reason for dispute in correct.   If the reason is correct then consult with TL and post TL’s alignment, highlight to internal IBC team for validation and advice member to wait for 24-48 hrs  If the dispute reason is not valid then give denial as per SOP

## 7c. 6E Skai Chatbot gave incorrect policy information

*Scenario:* As per the member the policy info shown by 6E Skai chatbot is not matching per the info mentioned in web- site/tnc

**SOP — steps:**
Greet member.  Request member to share his/her concern.  Probe the member regarding the policy info for which they are disputing it to be incorrect as shown by chatbot.  Verify the same info at our end by checking if the info given by 6E Skai chatbot is incorrect and not giving the info as per the tnc or info shown on the website.  In case the info shown is correct the educate the member on the same and guide by sharing the reference of the tnc/info mentioned on the website.  In case the info shown is incorrect , then apologize to the member check for the expectation of the member and basis that raise with the internal IBC Member experience team.

## 8. Tier Upgrade/Retention

## 8a. Tier Upgrade/Retention Request - Outside policy

*Scenario:* As per the member they are requesting for tier upgrade however it is not as per tnc of tier upgrade

T&C/Policy for Tier upgrade  IndiGo BluChip Program offers 3 Tier status: Blu 3, Blu 2, and Blu 1. Blu 3 is the entry level Tier. Qualification to a  	higher Tier is based on the combination of Spends and Qualifying Flights accumulated in the Member's IndiGo BluChip Account.  Tier Benefit of Tier Bonus IndiGo BluChips as a result of the Member’s Tier status is accrued only for Qualifying  Flights and Qualifying Spends on 6E Flights or 6E Codeshare Flights taken by the Member.  The Blu 3/ Blu 2 or Blu 1 Tier status is valid for 12 months from the date of upgrade or renewal. The Blu 3 Tier status is the base status which is valid for throughout the lifetime of the Member. However, Tier Benefits associated with Blu 3 are valid for a period of 12 months from the date of issuance and will be reviewed on each anniversary of the Blu 3 Tier.  In case of Tier downgrade/upgrade/retain, the old Tier Benefits, if not utilized, will be purged, and the Member will get new Tier Benefits as per the downgraded/upgraded/retained Tier.  The Blu 3/ Blu 2 or Blu 1 Tier status is valid for 12 months from the date of upgrade or renewal. The Blu 3 Tier status is the base status which is valid for throughout the lifetime of the Member. However, Tier Benefits associated with Blu 3 are valid for a period of 12 months from the date of issuance and will be reviewed on each anniversary of the Blu 3 Tier.  Members must accrue a minimum of INR 100,000 Spends and take a minimum of 4 6E Flights / 6E Codeshare Flights or accrue INR 200,000 Spends and take a minimum of 8 6E Flights / 6E Codeshare Flights, where the Spends will be calculated by taking into account the Qualifying Charges on Revenue Flights(Base fare+YQ) , in a 12-month rolling period to upgrade and/or retain a Blu 2 or Blu 1 Tier, respectively. | T&C/Policy for Tier upgrade  IndiGo BluChip Program offers 3 Tier status: Blu 3, Blu 2, and Blu 1. Blu 3 is the entry level Tier. Qualification to a  	higher Tier is based on the combination of Spends and Qualifying Flights accumulated in the Member's IndiGo BluChip Account.  Tier Benefit of Tier Bonus IndiGo BluChips as a result of the Member’s Tier status is accrued only for Qualifying  Flights and Qualifying Spends on 6E Flights or 6E Codeshare Flights taken by the Member.  The Blu 3/ Blu 2 or Blu 1 Tier status is valid for 12 months from the date of upgrade or renewal. The Blu 3 Tier status is the base status which is valid for throughout the lifetime of the Member. However, Tier Benefits associated with Blu 3 are valid for a period of 12 months from the date of issuance and will be reviewed on each anniversary of the Blu 3 Tier.  In case of Tier downgrade/upgrade/retain, the old Tier Benefits, if not utilized, will be purged, and the Member will get new Tier Benefits as per the downgraded/upgraded/retained Tier.  The Blu 3/ Blu 2 or Blu 1 Tier status is valid for 12 months from the date of upgrade or renewal. The Blu 3 Tier status is the base status which is valid for throughout the lifetime of the Member. However, Tier Benefits associated with Blu 3 are valid for a period of 12 months from the date of issuance and will be reviewed on each anniversary of the Blu 3 Tier.  Members must accrue a minimum of INR 100,000 Spends and take a minimum of 4 6E Flights / 6E Codeshare Flights or accrue INR 200,000 Spends and take a minimum of 8 6E Flights / 6E Codeshare Flights, where the Spends will be calculated by taking into account the Qualifying Charges on Revenue Flights(Base fare+YQ) , in a 12-month rolling period to upgrade and/or retain a Blu 2 or Blu 1 Tier, respectively. | T&C/Policy for Tier upgrade  IndiGo BluChip Program offers 3 Tier status: Blu 3, Blu 2, and Blu 1. Blu 3 is the entry level Tier. Qualification to a  	higher Tier is based on the combination of Spends and Qualifying Flights accumulated in the Member's IndiGo BluChip Account.  Tier Benefit of Tier Bonus IndiGo BluChips as a result of the Member’s Tier status is accrued only for Qualifying  Flights and Qualifying Spends on 6E Flights or 6E Codeshare Flights taken by the Member.  The Blu 3/ Blu 2 or Blu 1 Tier status is valid for 12 months from the date of upgrade or renewal. The Blu 3 Tier status is the base status which is valid for throughout the lifetime of the Member. However, Tier Benefits associated with Blu 3 are valid for a period of 12 months from the date of issuance and will be reviewed on each anniversary of the Blu 3 Tier.  In case of Tier downgrade/upgrade/retain, the old Tier Benefits, if not utilized, will be purged, and the Member will get new Tier Benefits as per the downgraded/upgraded/retained Tier.  The Blu 3/ Blu 2 or Blu 1 Tier status is valid for 12 months from the date of upgrade or renewal. The Blu 3 Tier status is the base status which is valid for throughout the lifetime of the Member. However, Tier Benefits associated with Blu 3 are valid for a period of 12 months from the date of issuance and will be reviewed on each anniversary of the Blu 3 Tier.  Members must accrue a minimum of INR 100,000 Spends and take a minimum of 4 6E Flights / 6E Codeshare Flights or accrue INR 200,000 Spends and take a minimum of 8 6E Flights / 6E Codeshare Flights, where the Spends will be calculated by taking into account the Qualifying Charges on Revenue Flights(Base fare+YQ) , in a 12-month rolling period to upgrade and/or retain a Blu 2 or Blu 1 Tier, respectively. | T&C/Policy for Tier upgrade  IndiGo BluChip Program offers 3 Tier status: Blu 3, Blu 2, and Blu 1. Blu 3 is the entry level Tier. Qualification to a  	higher Tier is based on the combination of Spends and Qualifying Flights accumulated in the Member's IndiGo BluChip Account.  Tier Benefit of Tier Bonus IndiGo BluChips as a result of the Member’s Tier status is accrued only for Qualifying  Flights and Qualifying Spends on 6E Flights or 6E Codeshare Flights taken by the Member.  The Blu 3/ Blu 2 or Blu 1 Tier status is valid for 12 months from the date of upgrade or renewal. The Blu 3 Tier status is the base status which is valid for throughout the lifetime of the Member. However, Tier Benefits associated with Blu 3 are valid for a period of 12 months from the date of issuance and will be reviewed on each anniversary of the Blu 3 Tier.  In case of Tier downgrade/upgrade/retain, the old Tier Benefits, if not utilized, will be purged, and the Member will get new Tier Benefits as per the downgraded/upgraded/retained Tier.  The Blu 3/ Blu 2 or Blu 1 Tier status is valid for 12 months from the date of upgrade or renewal. The Blu 3 Tier status is the base status which is valid for throughout the lifetime of the Member. However, Tier Benefits associated with Blu 3 are valid for a period of 12 months from the date of issuance and will be reviewed on each anniversary of the Blu 3 Tier.  Members must accrue a minimum of INR 100,000 Spends and take a minimum of 4 6E Flights / 6E Codeshare Flights or accrue INR 200,000 Spends and take a minimum of 8 6E Flights / 6E Codeshare Flights, where the Spends will be calculated by taking into account the Qualifying Charges on Revenue Flights(Base fare+YQ) , in a 12-month rolling period to upgrade and/or retain a Blu 2 or Blu 1 Tier, respectively.
SOP | SOP | SOP
Greet member.  Request member to share his/her concern.  Please check if member has any goodwill points in the account instead of retro claim points.  Probe the member regarding the reason for tier upgrade request and explain the criteria for upgrade  Check on LMS to validate the spends and 6E flights taken and basis the tier spends on LMS explain the member regarding their current tier and how much spends and flights to be taken for upgrade  In case if member is still requesting for tier upgrade and not meting the tnc then explain the policy inform the spends done in last 365 days basis which his tier upgrade is decided. If member still disputes, then share denial as per SOP. | Greet member.  Request member to share his/her concern.  Please check if member has any goodwill points in the account instead of retro claim points.  Probe the member regarding the reason for tier upgrade request and explain the criteria for upgrade  Check on LMS to validate the spends and 6E flights taken and basis the tier spends on LMS explain the member regarding their current tier and how much spends and flights to be taken for upgrade  In case if member is still requesting for tier upgrade and not meting the tnc then explain the policy inform the spends done in last 365 days basis which his tier upgrade is decided. If member still disputes, then share denial as per SOP. | Greet member.  Request member to share his/her concern.  Please check if member has any goodwill points in the account instead of retro claim points.  Probe the member regarding the reason for tier upgrade request and explain the criteria for upgrade  Check on LMS to validate the spends and 6E flights taken and basis the tier spends on LMS explain the member regarding their current tier and how much spends and flights to be taken for upgrade  In case if member is still requesting for tier upgrade and not meting the tnc then explain the policy inform the spends done in last 365 days basis which his tier upgrade is decided. If member still disputes, then share denial as per SOP.

## 8b. Tier Criteria met, Tier not Upgraded

*Scenario:* As per the member they met the conditions for the tier upgrade however the tier has not upgraded

**SOP — steps:**
Greet member.  Request member to share his/her concern.  Probe the member to understand as why they are referring that the tier has not been upgraded. Ask member for the flight count & spends according to which they are claiming that tier upgrade is not done. 4. Go to LMS for validation of flight count & spends for last 365 days as per current date.   Go to LMS>>>Member care >>> click on Loyalty tab under member check to see the tier spends. We can also check the spends & flights to be taken for the upgrade from current tier to next tier and inform the same to the member.  Under Loyalty Tab, click on “Trackers” on same page to see the Transaction count. The transaction count reflecting is in last 365 days  If in case as per our validation there is discrepancy in the flight taken & spends due to which the tier upgrade has not happened, then take LMS screenshot and relevant screenshot from member & raise to Program ops  In case of no discrepancy, educate member that for tier upgrade, we consider flight taken & spends within  the last 365 days and not the lifetime spends and flight taken.

## 9.IndiGo BluChips Expiry related

IndiGo BluChips Expiry Policy  All IndiGo BluChips have a validity of 24 (Twenty-Four) months from the date of their accrual. Once they have expired, they cannot be reinstated.  These IndiGo BluChips will be reviewed at the end of each calendar month. If the current month for review is   September 2026, the IndiGo BluChips accumulated in the Member’s IndiGo BluChip Account shall remain valid if the   Member has performed at least 1 Accrual Activity or Award/Redemption Activity in the preceding 24 months from the current month of review (i.e., between October 1, 2024 to September 30, 2026). Since the last Accrual Activity   	or Award/Redemption Activity made by the Member falls within this 24-month period, the IndiGo BluChips shall remain valid for another 30 (Thirty) calendar days. This process shall repeat itself the following month.

## 9a. Query on IndiGo BluChips Expiry

*Scenario:* Member is enquiring that when will my IBC’s will expire?  → Do IndiGo BluChips earned on Program Partners have a different expiry than IndiGo BluChips earned for IndiGo flights?

**SOP — steps:**
Greet member.  Request member to share his/her concern.  Advise the member as per the Program policy tnc or refer to the policy as mentioned above regarding the BluChips validity

**Screen reference — LMS Incentives - Expiration tab showing IndiGo BluChips expiry schedule:**

LMS member profile screen for member "Deepak Vasandani" (Verified), showing the Incentives tab with the Expiration sub-tab open, used to check IndiGo BluChips expiry dates.

Member details panel (left):
- FFN: 031006673
- Mobile: +919909004679
- Email: deel_vasandani@yahoo....
- Member since Mar 19, 2025
- Default program: Blu 3 (Default program for I...)
- Total Lifetime Spends: Rs.229,910
- Active coupons: "Oops! This customer has no active coupon"
- Recent Activities: e.g. Ticket number R53HPS_0310066..., Rs.3,185.00, Dec 8, 2025 5:30 PM

Agent steps:
1. Open the member profile and click the "Incentives" tab (top navigation: Profile, Loyalty, Activity, Incentives, Communications).
2. Click the "Expiration" button (highlighted) among Transactions / Expiration / Coupons / Other promotions / Gift vouchers.
3. Use the "Expiry schedule" view (other views available: Conversion schedule, Trigger based IndiGo BluChips).
4. Review the expiry schedule list (program "Indigo ProdDefaultProgram", all marked "Fixed"):
   - Jul 31, 2027 -> 2,207
   - Aug 31, 2027 -> 1,405
   - Sep 30, 2027 -> 481 (selected/highlighted)
   - Nov 30, 2027 -> 1,022
   - Dec 31, 2027 -> 255
5. Click a schedule entry (e.g. Sep 30, 2027) to see its breakdown on the right ("Indigo ProdDefaultProgram", Sep 30, 2027, Fixed):
   - IndiGo BluChips summary: 481
   - Ticket Miles: 0
   - Ticket promotional IndiGo BluChips: 0
   - Line-level IndiGo BluChips: 0
   - Line-level promotional IndiGo BluChips: 481
   - Customer promotional IndiGo BluChips: 0

## 9b. Activity done, IBCs expiry date not extended

*Scenario:* As per the member they have done activity however the IBCs still expired and not extended

**SOP — steps:**
Greet member.  Request member to share his/her concern.  Go to LMS and check for the date on which the IBCs expired and the last activity (Accrual or Redeem) date.  Check the span between the expiry date of IBC’s and the last activity date  In case there is gap of less than 24 months between the date of expiry of IBC and activity date, raise to Program Ops  In case the gap is more than 24 months and IBC’s have expired then explain policy for the expiry of IBC’s
Step 1: Go to LMS>Member care and click on “Activity” tab to check the last activity date
Step 2: Go to LMS>Member care and click on “Incentives” tab to check the last activity date. Under Activity tab click on
“Expiration” tab

## 9c. Expiry date extension - Out of policy request

*Scenario:* Member IBC's have expired due to no activity in last 24 months from the accrual date and requesting for extension of the expiry  date

**SOP — steps:**
Greet member.  Request member to share his/her concern.  Advise the member regarding the policy for expiry of IndiGo BluChips query   In case the member still disputes/escalates or is a high profile member then check with TL if any empowerment available and basis TL’s guidance, raise this to IBC 6E spoc for any exception.

## 10. Reporting of fraudulent activity in my account

## 10. Member reported fraud

*Scenario:* Account Takeover: Unauthorized access, IndiGo BluChips Theft, Identity Theft, Phishing Attacks, Data Breach, Reward Abuse, Partner Fraud, Insider Fraud  → I noticed unauthorized transactions on my loyalty account. I called member care to report it and request a refund  → I've suffered significant financial loss due to some fraud

**SOP — steps:**
Greet & verify member  Request member to share concern. Ask the member to describe the issue they are facing, including details of the unauthorized transactions or fraud.  Ask for specific details such as transaction dates, amounts, and any suspicious activities noticed.  Check from member if he wants to lock the account immediately. If yes, please raise it immediately to Prog. Ops team or Cyber-crime team within IndiGo. If applicable, suggest member to log a complaint with cyber-crime dept. of law enforcement agencies.  If the understanding of issue requires more clarification, then ask the member if they can share screenshots or any evidence of the unauthorized transactions via email. If yes, request member to share the error screenshot on the case/ticket acknowledgment email which he would have received.  Upon receiving the details from the member, escalate the issue to the concerned team as per the escalation matrix.( CC  Team supervisor to call Program OPS for informing before moving the case)  Inform the member that their concern has been highlighted to the relevant team and provide them with a case/ticket reference number.  Closing Statement.

## 11. Delete/Deactivate Account

S. No. | Topic | Key/Scenario

## 11a. Not interested in Program / Don’t want  IBC account

*Scenario:* Member is randomly saying that he/she is not interested in the IBC Program

## 11b. Data Privacy/Security issues

*Scenario:* Member wants to delete the account due to data privacy issues or wants to delete the trip history

## 11c. Not a Frequent Traveler

*Scenario:* Member is not a FF (Frequent Flyer) and requesting for deletion of IBC Account

## 11d. Too Many Promotional Emails or Notifications

*Scenario:* Member is irated with so many promotional/sales campaign emails and due to frustration, he is re- questing to delete the IBC account

## 11e. Account created without consent

*Scenario:* Member has shared the request as his account has been created without his/her consent, may be  his/her TA, Or any other family member and now requesting to delete his/her account

## 11f. Created by mistake

*Scenario:* Member created the account by mistake with the incorrect details and requesting for deletion of IBC Account

## 11g. Difficult User Experience on App/Web

*Scenario:* Member is irate as he/she finds our web/app experience very difficult. For Example - Member  sharing his concern that why WhatsApp does not  have the feature of IBC BURN booking creation  feature

## 11h. Want to delete Trip History

*Scenario:* Member wants to delete the account due to data privacy issues or wants to delete the trip history

## 11i. Frustration due to policy denial

*Scenario:* Member requested for retro claim for a PNR outside 90 days and IBC team denied the request as  per SOP. Now, member is disappointed because of  the denial, member wants to delete his/her ac- count

## 11j. Customer Service Issues/ CC Mishandling

*Scenario:* Member had a horrible experience at airport/Inflight/Call Centre/ MHB and because of that experience, member Is requesting to delete his/her ac- count

**SOP — steps:**
Member reaches out with an account deactivation, deletion, or closure request from registered credentials. If member reaches out with unregistered credentials, expert to request member to share the request from registered credentials.  Expert must outcall the member to understand the reason for account deletion and advise all the implications that will occur due to account deletion.  In case, member has not provided reason for account closure/deletion in writing. TL must connect with member & find out reason.    If the member insists on deletion due to customer service or policy denial issues or difficult user experience, the Team Leader should investigate the case in detail and connect with the member to avoid churn.  Expert must explain the implications of account closure/deletion using the approved email template and obtain written consent from the member.  Expert/Team Leader must then raise the request to Program Ops, including the member’s trail email showing written consent and the reason for account deletion.  Incase the reason highlighted by member for account deletion is customer service issues, difficult user experience, or policy denial, then TL to give approval in writing with reason while sharing the request to program ops team.  If reason for account closure/deletion is provided by member in writing as “Account created by mistake / Data security/privacy issues / Not a frequent traveler / Account created without consent / other reasons), Team leader approval is not required.    Request the member to allow up to 5 working days for processing. Once confirmation is received from Program Ops, send a final confirmation email using the approved template.

## Systems & tools (screen reference)

*Transcribed from SOP screenshots — the LMS / Member Care / Salesforce / IndiGo website screens agents use to action these requests.*

**Screen reference — Capillary Sign In (Okta) Login Screen:**

UI Screenshot: Capillary platform Sign In page (authenticated via Okta).

What the screen shows and what the agent should do:
1. Navigate to the Capillary login page (branded "capillary", "Powered by Okta" at bottom left).
2. In the "Username" field, enter your work email address (example shown: alok.mishra1@igtsolutions.com).
3. Optionally tick the "Remember me" checkbox.
4. Click the blue "Next" button to proceed to the password/authentication step.
5. If you cannot access your account, click the "Need help signing in?" link below the Next button.

Visible links/labels: "Sign In", "Username", "Remember me", "Next", "Need help signing in?", "Powered by Okta", "Privacy Policy".

**Screen reference — LMS Home Dashboard - Indigo UAT (Welcome back, rohit):**

UI screenshot: Loyalty Management System (LMS) home/landing dashboard after login.

1. Top bar shows "Home" with the app grid icon (top-left), the workspace selector "Indigo UAT", a settings (gear) icon and a user profile icon (top-right).
2. Main area: "Welcome back, rohit" heading.
3. "Get started" section with three tiles, each having a "Know more" link:
   - View Insights
   - Launch a loyalty program
   - Create a campaign
4. "Explore features" section below with a carousel (paged dots).
5. Right-side "Quick Links" panel:
   - Live Campaigns: Outbound (00), DVS (00), Referral (00)
   - Loyalty Programs (01)
   - Customer Requests - Pending (00)
   - SMS Credits: 0, with an "Add Credits" link
6. A floating green action button at the bottom-right.

Agent action: This is the LMS landing page. From here the agent navigates to the relevant module (e.g., Loyalty Programs, Customer Requests) to begin handling a member account request.

**Screen reference — Member Care - Member Search screen:**

UI screenshot of the Member Care application (environment indicator: "Indigo UAT") showing the Member Search screen.

1. Top header shows the "Member Care" app title, environment label "Indigo UAT", and notification, settings, and profile icons on the right.
2. Left navigation panel under "Member care" contains:
   - Members
   - Custom Actions (expandable)
   - Requests (expandable)
   - CC & Program Ops (expanded), with sub-items:
     - Customer Support
     - Contact Center
3. A banner note reads: "...incentives search, profile logs and leads information, please visit the old Member care." with a link "Open old Member Care".
4. Center of the screen shows the "Member Search" heading.
5. Below it is a search bar with a category dropdown defaulting to "Customers" and a search input with placeholder: "Search using name, mobile (with country code), email or FFN". A hint below reads "Enter complete identifier".
6. Below an "OR" divider is a "+ Member Enrollment" link to enroll a new member.

Agent action: To look up a member, ensure the search category is set to "Customers", then type the member's complete identifier (name, mobile with country code, email, or FFN) into the search bar. To register a new member instead, click "+ Member Enrollment".

**Screen reference — Member Care - Member Search screen:**

UI screenshot: Member Care application (Indigo UAT environment) - "Member Search" screen.

What the screen shows and what the agent should do:

1. Top header shows "Member Care" app with environment "Indigo UAT", plus notification, settings, and profile icons on the right.
2. A banner note reads: "For requests management, incentives search, profile logs and leads information, please visit the old Member care." with a link "Open old Member Care".
3. Center of the screen has the "Member Search" panel with a search bar:
   - A dropdown set to "Customers" (used to choose the search type/field).
   - A text input where the agent types the member identifier; here it contains "000014221".
   - An "X" button to clear the search input.
4. Below the search bar, a matching result is shown: avatar "AM", member name "Alok Mishra", with the highlighted FFN/Customer ID "000014221". The agent clicks this result to open the member's profile.
5. Below the result, separated by an "OR" divider, there is a "+ Member Enrollment" link to enroll a new member instead of searching.

Agent action: Select the search type in the "Customers" dropdown, enter the member's Customer ID / FFN in the search box, then click the matching member record (e.g., "Alok Mishra - 000014221") to open the account. Use "+ Member Enrollment" only when creating a new member.

**Screen reference — Member Care - Loyalty tab (Account / Tier / Miles details):**

UI screenshot: Member Care (LMS) member detail page, **Loyalty** tab selected (Indigo UAT environment). Used to look up a member's account and transaction details.

What the screen shows:
1. Left panel - member identity card:
   - Status badge "Verified", Name: Alok Mishra, "Member since Sep 4, 2024"
   - FFN: 000014221
   - Mobile: +917311110389
   - Email: alok.mishra1@igtsolutions... (truncated)
   - "Communication channels" expandable dropdown
   - Total Activities: ₹5,394
   - Program tile: "Blu 3 - Default program for I..." with a refresh icon
   - "Active coupons" (View all): Prime Pass X3GBV7 (₹0 Off), Prime Pass 0CBDM0
   - "Recent Activities" (View all): ACTIVITY ₹3,193.00, Ticket number CPTNHC_0000142..., Sep 7, 2024 11:45 AM, Miles Accrued: 383; a second activity (Sep 6, 20...)
2. Top tab bar: Profile | Loyalty (active) | Activity | Incentives | Communications, plus refresh and "..." (more) icons.
3. Right panel - Loyalty details:
   - **Tier Status** (with "View tier history" link): badge "Blu 3 - valid till Sep 4, 2124"
   - **Remaining to Upgrade**: "Customer will reach Blu 2 by satisfying any conditions"
     - Condition 1: "If Tier_Points based on ALTERNATE_CURRENCIES increases by 94606" (progress bar)
     - OR
     - Condition 2: "If transactioncount based on Ticket Value increases by 2" (progress bar)
   - **Program Summary** (with "View details" link):
     - Miles Balance: 211,090 / Redeposited Miles: 0
     - Miles Balance: 300,647 / Adjusted Miles: 0
     - Redeemed: 89,557 / Pending Miles: 0
     - Expired: 0 / Lifetime spend: ₹5,394
   - Collapsible sections: Trackers, Coalition Loyalty, Supplementary Membership, Targets

Agent action: Open the member record in Member Care and use the Loyalty tab to read tier status, miles balance, expiry, recent activities and transaction details when answering an account information enquiry. Use "View tier history", "View details", and the section dropdowns (Trackers/Coalition Loyalty/Supplementary Membership/Targets) for more detail.

**Screen reference — IndiGo Website - Logged-in Member Account Menu:**

UI screenshot of the IndiGo website (logged-in member view) showing the top navigation and the account dropdown panel.

What the screen shows:
1. Top navigation bar: IndiGo logo, "Book", "Trips", "Deals and Offers", "Check-in", "IndiGo BluChip" (dropdown), "Tariff Sheet" (link), and "IndiGo BluChips Balance 0".
2. The account/menu dropdown panel is open, with three columns:
   - "Your Information": Flight Status, My Scratch Card, 6E Rewards.
   - "Other information": About us, Contact us, WhatsApp, Terms and Conditions, Help and FAQs.
   - "My Orders": Sight Seeing (New), Experiences (New).
3. Member profile box (right side, highlighted): "Hello Anik Kumar", "IndiGo BluChip Membership No. 047609100", phone "7004544816", email "anikkumarsingh@gmail.com".
4. Account action buttons: "My Profile", "Dashboard", "My Nominees", "Log Out".

Agent actions:
- Click "My Profile" to view/edit the member's profile details.
- Click "Dashboard" to view the loyalty dashboard/account information.
- Click "My Nominees" to view or manage nominee details.
- Use "Terms and Conditions" / "Help and FAQs" under "Other information" to reference policy.

**Screen reference — Welcome to IndiGo BluChip - Member Dashboard:**

UI screenshot of the IndiGo BluChip member dashboard ("Welcome to IndiGo BluChip") showing account/profile details the agent can reference for an Account Information enquiry.

What the screen shows:
1. Top navigation bar with menu items: Book, Trips, Deals and Offers, Check-in, IndiGo BluChip; plus an "IndiGo BluChips Balance 0" indicator and a profile/account dropdown (avatar "a") on the right.
2. Left profile card:
   - Tier badge: "IndiGo BluChip Blu 3 Member"
   - Greeting: "Hi anik kumar"
   - "IndiGo BluChip Membership No.: 047609100"
   - Contact line: "917004544816 | anikkumarsingh@gmail.com"
   - A "Home >" button.
3. Right card: large "0" with label "IndiGo BluChips Balance" and a blue "Earn Now" call-to-action button.
4. Bottom: a "Tier Benefit" section banner.

Agent action: Use this dashboard view to read out / verify the member's account details — membership number (FFN), tier (Blu 3), registered mobile number, registered email, and current IndiGo BluChips balance.

**Screen reference — IndiGo BluChip Member Dashboard - Welcome / Account Overview:**

UI screenshot: IndiGo BluChip member dashboard ("Welcome to IndiGo BluChip") showing the member's loyalty account overview. Agent uses this screen to read out / verify a member's account information.

Top navigation bar: IndiGo logo, "Book", "Trips", "Deals and Offers", "Check-in", "IndiGo BluChip" (dropdown), and a top-right pill showing "IndiGo BluChips Balance 19,253" plus a profile avatar ("A").

Member profile card (left):
1. Tier badge: "IndiGo BluChip Blu 2 Member".
2. Greeting: "Hi Alok M Alo".
3. "IndiGo BluChip Membership No.: 000014221".
4. Contact details: "917311110389 | alokmishra.sh@gmail.com".
5. "View Profile >" button — click to open the full member profile.

Middle summary panel:
- "IndiGo BluChips expiring soon: 0" with a "View Summary >" link.
- "Lifetime Redemptions: 2,49,851" with a "View Summary >" link.

Right balance panel:
- "19,253" — "IndiGo BluChips Balance".
- "Redeem Now" button.

Page-level actions: "SHARE FEEDBACK" link (top right). Tabs below the cards toggle between "Tier Benefit" (selected) and "Partnerships". Lower section heading: "WHAT YOUR INDIGO BLUCHIP BLU 2 MEMBERSHIP CAN DO?" / "Your Tier Benefits".

Agent action: Use this dashboard to confirm and share account/balance details — membership number, tier, contact info, current BluChips balance, expiring-soon count, and lifetime redemptions. Click "View Profile" for profile details or "View Summary" for transaction/expiry detail.

**Screen reference — Transaction History page (IndiGo BluChip dashboard):**

UI screenshot: IndiGo BluChip member dashboard — "Transaction History" page.

What the screen shows:
1. Top navigation bar with menus: Book, Trips, Deals and Offers, Check-in, IndiGo BluChip. Top-right shows "IndiGo BluChips Balance 19,253" and the member's account avatar.
2. A "< BACK TO DASHBOARD" link at the top-left to return to the main dashboard.
3. Page heading "Transaction History" with summary figures:
   - Total IndiGo BluChips Earned: 85,065
   - Life Time Redemptions: 2,72,221
4. A "Download Summary" button (top-right) to download the transaction summary.
5. Three tabs: All Transactions (selected), IndiGo BluChip, Partners.
6. Filter chips: All Transactions (selected), Earned, Promised, Redeemed, Expired. Sort and filter icons appear on the right.
7. A list of transaction entries, each with type, date, and chip amount:
   - IndiGo BluChips Redeemed — 20 Nov 2025 — -3,058
   - IndiGo BluChips Credited — 03 Nov 2025 — +204
   - IndiGo BluChips Credited — 24 Oct 2025 — +100
   Each entry has an expand (chevron) control to view details.

Agent actions: To check a member's account/transaction details, open the member dashboard and click "IndiGo BluChip" / go to Transaction History. Use the filter chips (Earned/Promised/Redeemed/Expired) to narrow results, the tabs (All Transactions / IndiGo BluChip / Partners) to scope the source, and "Download Summary" to export the transaction summary.

**Screen reference — Salesforce Case Details - Fetch Profile:**

Salesforce case-management screen for an IndiGo BluChip case. Agent actions:

1. Top status bar shows the case lifecycle stages: Open -> Awaiting (Department) -> Received Response (Department) -> Awaiting (Customer) -> Received Response (Customer) -> Reopen -> Resolved. Current stage highlighted: "Open".
2. Left "Case Details" panel shows fields: Case Number (21883878), Status (Open), Age (9), Consent To Complete Open Tasks (checkbox), Parent Case, RC Checked (checkbox), IndiGo Stretch (checkbox), 6e Dept (IndiGo BluChip), PNR No (VU75TZ), Reopen Tag, Source of Booking, Mobile No.
3. Right panel header shows Case 21883878 with action buttons: "Send Upload File Link", "Fetch PNR Detail", "Fetch Mobile PNR" (plus a dropdown). Below: Status (Open), Loyalty Tier, Member Type, Loyalty Number fields (blank).
4. Tab row: Feed | Details | Related. The "Details" tab is highlighted (red box) - click it to open profile details.
5. Click the blue "Fetch Profile" button to retrieve the member's Customer Profile Details (the "Customer Profile Details" section appears collapsed below).

**Screen reference — Salesforce Case Details - Fetch Profile:**

UI screenshot of the Salesforce case management screen for an IndiGo BluChip case.

Top: Case progress lifecycle bar with stages: Open -> Awaiting (Department) -> Received Response (Department) -> Awaiting (Customer) -> Received Response (Customer) -> Reopen -> Resolved. Current stage highlighted: Open.

Left panel - Case Details:
- Case Number: 21883878
- Status: Open
- Age: 9
- Consent To Complete Open Tasks: (checkbox, unchecked)
- Parent Case: (blank)
- RC Checked: (checkbox, unchecked)
- IndiGo Stretch: (checkbox, unchecked)
- 6e Dept: IndiGo BluChip
- PNR No: VU75TZ
- Reopen Tag: (blank)
- Source of Booking: (blank)
- Mobile No.: (blank)

Right panel - Case 21883878:
- Buttons (top right): Send Upload File Link, Fetch PNR Detail, Fetch Mobile PNR
- Fields: Status: Open | Loyalty Tier | Member Type | Loyalty Number
- Tabs: Feed | Details (selected) | Related

Agent action:
1. Open the Details tab of the case.
2. Click the highlighted blue "Fetch Profile" button (outlined in red) to retrieve the member's Customer Profile Details.
3. The "Customer Profile Details" section expands below once the profile is fetched.

**Screen reference — Salesforce Case Details - Related tab, Add Files:**

Salesforce Case Details screen for an IndiGo BluChip Loyalty Case.

What the screen shows:
1. Left panel "Case Details" with fields including Case Number (21883878), Status (Open), Age (19), 6e Dept (IndiGo BluChip), PNR No (VU75TZ), Mobile No. (8512848080), Email, Case Owner (Anjum(6E)), LOB Queue (IndiGo BluChip Master Queue), User Identifier (IndiGo User), Priority (Medium), and other editable fields.
2. Top tabs in the center: Feed, Details, and "Related" (the Related tab is highlighted/selected).
3. Center panel sections: "Case History (6+)" listing record-lock/case-owner/record-type changes with Date, Field, User, Original Value, New Value columns; "Activity History (0)" with Log a Call / View All buttons; "Case Comments (0)" with a New button; and "Files (1)" showing an attached file "Nice Application Snapshot" (08-Oct-2025, 123KB, png).
4. The "Add Files" button (highlighted in red) is in the Files section.
5. Right panel: "Approval History (3+)" showing approval requests (e.g., Approval from CC Partner - IGT, Approval Request Submitted, Approved), plus action buttons "LMS" and "CIAM Details".

Agent action: Open the "Related" tab on the Case, scroll to the Files section, and click "Add Files" to attach a supporting document/snapshot to the case.

**Screen reference — Loyalty CIAM fields panel:**

## Loyalty CIAM fields (CRM/Salesforce panel)

The screen shows an expandable "Loyalty CIAM fields" section displaying the member's loyalty profile data. Each field has a pencil (edit) icon on the right to modify the value.

Fields shown:
1. Loyalty Identifier (checkbox, unchecked)
2. Loyalty First Name (empty)
3. Loyalty Last Name (empty)
4. Loyalty Number (empty)
5. Loyalty Tier (empty)
6. Loyalty Case (checkbox, unchecked)
7. Loyalty Email Id (empty)
8. Contact Country Code: +91
9. Loyalty Mobile: 9823240552 (shown as a hyperlink)

Agent action: Use the pencil/edit icon next to the relevant field to view or update the member's loyalty (CIAM) profile details such as name, loyalty number, tier, email, country code, and mobile number.

**Screen reference — Loyalty CIAM fields panel:**

UI screenshot of the "Loyalty CIAM fields" panel (collapsible section) in the CRM/Salesforce member record, showing the member's loyalty profile fields. Each field has a pencil (edit) icon on the right to update its value.

Fields shown (left column):
1. Loyalty Identifier — (checkbox, unchecked) — pencil/edit icon
2. Loyalty First Name — Firoz — pencil/edit icon
3. Loyalty Last Name — Raja — pencil/edit icon
4. Loyalty Number — 042085621 — pencil/edit icon
5. Loyalty Tier — Blu 3

Fields shown (right column):
6. Loyalty Case — (checkbox, unchecked) — pencil/edit icon
7. Loyalty Email Id — firozraja8@gmail.com — pencil/edit icon
8. Contact Country Code — +65 — pencil/edit icon
9. Loyalty Mobile — 84537177 — pencil/edit icon

Agent action: Expand the "Loyalty CIAM fields" section to view the member's loyalty account details (name, loyalty number, tier, email, country code, mobile). Click the pencil (edit) icon next to a field to update that field's value.

**Screen reference — IndiGo BluChip Member Account Home / Profile Navigation:**

UI screenshot of the IndiGo BluChip member account landing/profile screen.

Screen contents:
1. Top bar shows "Tariff Sheet" link, "IndiGo BluChips Balance 0", and an account avatar with a dropdown toggle.
2. Greeting: "Hello Anik Kumar".
3. Member details displayed:
   - IndiGo BluChip Membership No. 047609100
   - 7004544816 (mobile number)
   - anikkumarsingh@gmail.com (email ID)
4. Two "New" badge labels appear on the left side panel.

Action buttons available to navigate:
- "My Profile" — view/edit profile details.
- "Dashboard" — view loyalty dashboard/account info.
- "My Nominees" — view/add/manage nominee details.
- "Log Out" — sign out of the account.

Agent guidance: Direct the member to click the relevant button — "My Profile" to view/update profile fields, "Dashboard" to check IndiGo BluChips balance and transactions, or "My Nominees" to manage nominees.

**Screen reference — LMS Member Profile - Activity Tab (Transaction Details):**

UI screenshot of the LMS member profile screen, with the "Activity" tab selected, used to look up a member's account and transaction/accrual details.

What the screen shows and what the agent does:

1. Left panel - member identity card:
   - Member name: "Alok M Alo" with a green "Verified" badge.
   - "Member since Sep 4, 2024".
   - FFN: 000014221
   - Mobile: +917311110389
   - Email: alokmishra.sh@gmail.com
   - Expandable "Communication channels" section.
   - "Total Lifetime Spends" label (value below, partly cut off).

2. Top tab bar: Profile | Loyalty | Activity (currently selected) | Incentives | Communications. Top-right has a refresh icon and a "..." (more options) menu.

3. Activity sub-filter chips: "Activity" (selected/blue) | Behavioral events | Milestones | Rewards catalog | Audit logs (scroll arrow ">" to see more).

4. Activity transaction list (middle column):
   - Ticket number CPTNHC_000014221DELAM... - Sep 7, 2024 11:45 AM - ₹3,193 (this row is selected/highlighted).
   - Ticket number A1UU9H_000014221DELLKO... - Sep 6, 2024 12:55 PM - ₹2,201.

5. Right detail panel (for the selected transaction):
   - Ticket number: CPTNHC_000014221DELAMD2024-09-07T11:45:00
   - Status tag: "ACTIVITY" (green) and "NORMAL".
   - Sep 7, 2024 11:45 AM | "Evaluation log" link (opens in new tab).
   - "Accrual details" section: Net Miles 3,576.
   - Expandable "IndiGo BluChips summary" section.

Agent action: Use this Activity tab to verify the member's identity (FFN, name, contact) and to review individual transaction/ticket accrual details (ticket number, date, spend amount, net miles earned, evaluation log) when handling an account information or transaction details enquiry.
