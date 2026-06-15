"""Email templates for the BluChip Merge Account workflow.

Encodes the 10 SOP email templates as ``TEMPLATES: dict[str, dict]`` keyed
``T1``..``T10`` (per CONTRACTS.md sections 3.3 and 6).

Each template value has the shape::

    {
        "name": str,
        "description": str,
        "audience": "member" | "internal",  # T1-T9 member, T10 internal
        "subject": str,
        "body": str,
        "fields": list[str],                # placeholder names used in body
    }

Masking is per-template via each template's optional ``mask_fields`` list — the
SOP masks exactly one cross-disclosure: the OTHER account's email in T2
(``other_account_email`` -> ``abc***@gma.com``). A template with no
``mask_fields`` (the default) shows all its fields in full, because the remaining
emails/mobiles are shown to the verified owner of that account (T3/T4 mobiles, T9
re-login email/phone) or are internal (T10).

The wording of the legally-worded member-facing sentences is copied verbatim from
the source SOP (``format (1).txt``); only the bracketed slots have been converted
to snake_case ``{placeholders}``.

This module imports with no side effects.
"""

from __future__ import annotations

# The two-variant opener shared by member templates that begin with the
# "If Contact Established / If Unable to Contact after Three Attempts" header.
_CONTACT_OPENER: str = (
    "[If contact established] Thank you for your time over the phone.\n"
    "[If unable to reach the member after three attempts] We attempted to "
    "contact you on your registered mobile number {primary_phone} at {call_time}; "
    "however, we were unable to get through as the call went {call_reason}."
)


TEMPLATE_LABELS: dict[str, str] = {
    "T1": "request to resend from the registered email",
    "T2": "primary-mobile confirmation & consent request",
    "T3": "consent request to the other account",
    "T4": "interim 'under review' update",
    "T5": "denial — verification/DPA failed on the other account",
    "T6": "co-brand-linked denial (offer to make that account Primary)",
    "T7": "name-mismatch denial",
    "T8": "denial — DPA failed on the other account",
    "T9": "successful-merge resolution",
    "T10": "internal Program Ops request",
}


def template_label(template_id: str) -> str:
    """Plain-English name for a template id (falls back to the id itself)."""
    return TEMPLATE_LABELS.get(template_id, template_id)


TEMPLATES: dict[str, dict] = {
    "T1": {
        "name": "Merge Accounts_Member has 2IBC accounts",
        "description": "Request to share the request from reg Email_Member",
        "audience": "member",
        "subject": "Action required: Please resend your merge request from your registered email",
        "body": (
            "Dear {member_last_name},\n\n"
            + _CONTACT_OPENER
            + "\n\n"
            "Thank you for reaching out to us. We understand that you would like to "
            "merge your IndiGo BluChip Account, and we are here to assist you.\n\n"
            "For your account security, we can process requests only when they are "
            "received from the registered email address linked to your IndiGo "
            "BluChip Account.\n\n"
            "We noticed that your current request was sent from an email ID that "
            "does not match the one registered with your IndiGo BluChip Account.\n\n"
            "Please resend your request from your registered email address so that "
            "we may proceed further. Once we receive your request from the "
            "registered email ID, we will be happy to assist you promptly.\n\n"
            "If you are unsure of your registered email, you may log in to your "
            "IndiGo BluChip Account using your registered mobile number to view "
            "your profile details.\n\n"
            "If you have any questions or need additional support, please feel free "
            "to contact us, we're always here to help.\n\n"
            "Thank you for choosing IndiGo BluChip.\n\n"
            "Regards,\n"
            "{agent_name}\n"
            "Member Support Team\n"
            "IndiGo BluChip"
        ),
        "fields": [
            "member_last_name",
            "primary_phone",
            "call_time",
            "call_reason",
            "agent_name",
        ],
    },
    "T2": {
        "name": "Merge Accounts_Member has 2 IBC accounts",
        "description": "Confirmation of Primary IBC A/C Mobile No._Member",
        "mask_fields": ["other_account_email"],
        "audience": "member",
        "subject": "Please confirm your Primary IndiGo BluChip Account mobile number",
        "body": (
            "Dear {member_last_name},\n\n"
            + _CONTACT_OPENER
            + "\n\n"
            "To proceed, we kindly request you to confirm the mobile number you "
            "wish to retain as your primary IndiGo BluChip Account. Please note "
            "that the IndiGo BluChip Account linked to the selected mobile number "
            "(shared by you) will be treated as the Primary IndiGo BluChip Account. "
            "Once we receive your confirmation, your request will be reviewed in "
            "accordance with the IndiGo BluChip Program guidelines to determine "
            "whether the merger is permissible. If eligible, we will then proceed "
            "with merging the other account into the Primary account.\n\n"
            "For security purposes and to verify account ownership, consent is "
            "required from the registered email IDs of both accounts. Accordingly, "
            "a consent email has been sent to the registered email ID of other "
            "account ({other_account_email}).\n\n"
            "We request you to kindly reply to:\n"
            "• The consent email sent to your other account, and\n"
            "• This email confirming the mobile number you wish to retain as "
            "your Primary account.\n\n"
            "If you have any questions or need further assistance while providing "
            "consent, please reply to this email or call our support team at "
            "01246173838 and we will be happy to help.\n\n"
            "Regards,\n"
            "{agent_name}\n"
            "Member Support Team\n"
            "IndiGo BluChip"
        ),
        "fields": [
            "member_last_name",
            "primary_phone",
            "call_time",
            "call_reason",
            "other_account_email",
            "agent_name",
        ],
    },
    "T3": {
        "name": "Merge Accounts_Member has 2IBC accounts",
        "description": "Outbound email to Other account for consent_Member",
        "audience": "member",
        "subject": "Consent requested: Merge of your IndiGo BluChip account",
        "body": (
            "Dear {member_last_name},\n\n"
            "[Mandatory Outcall before this email] Thank you for your time over "
            "the phone.\n\n"
            "We are writing to request your consent to merge the IndiGo BluChip "
            "account registered to this email address with another IndiGo BluChip "
            "account. Please review the details below and confirm your consent by "
            "replying to this email from this address.\n\n"
            "Primary account (to remain active)\n"
            "• Membership number: {primary_membership_no}\n"
            "• Mobile Number: {primary_phone}\n\n"
            "Secondary account (to be merged)\n"
            "• Membership number: {secondary_membership_no}\n"
            "• Mobile Number: {secondary_phone}\n\n"
            "Please reply to this email sharing your consent. Once we receive your "
            "reply from this registered email address, we will review and notify "
            "you of the next steps.\n\n"
            "If you did not request this merge request or have any questions, "
            "please reply to this email or call our support team on 01246173838 "
            "before providing consent.\n\n"
            "Regards,\n"
            "{agent_name}\n"
            "Member Support Team\n"
            "IndiGo BluChip"
        ),
        "fields": [
            "member_last_name",
            "primary_membership_no",
            "primary_phone",
            "secondary_membership_no",
            "secondary_phone",
            "agent_name",
        ],
    },
    "T4": {
        "name": "Merge Accounts_Member has 2 IBC accounts",
        "description": "Interim email after consent received from both accounts_Member",
        "audience": "member",
        "subject": "Update: Your IndiGo BluChip merge request is under review",
        "body": (
            "Dear {member_last_name},\n\n"
            "Thank you for providing your consent to merge your two IndiGo BluChip "
            "Accounts. Your request will be reviewed by internal team in accordance "
            "with the IndiGo BluChip Program guidelines to determine whether the "
            "merger is permissible. If eligible, we will then proceed with merging "
            "the other account into the Primary account.\n\n"
            "Primary IndiGo BluChip Account (to remain active)\n"
            "• IndiGo BluChip ID: {primary_membership_no}\n"
            "• Mobile Number: {primary_phone}\n\n"
            "Secondary IndiGo BluChip Account (to be merged)\n"
            "• IndiGo BluChip ID: {secondary_membership_no}\n"
            "• Mobile Number: {secondary_phone}\n\n"
            "Please allow up to 72 working hours for an update.\n\n"
            "Should you have any further questions or require assistance, please "
            "feel free to reach out on 01246173838. Our team is always here to "
            "support you.\n\n"
            "Regards,\n"
            "{agent_name}\n"
            "Member Support Team\n"
            "IndiGo BluChip"
        ),
        "fields": [
            "member_last_name",
            "primary_membership_no",
            "primary_phone",
            "secondary_membership_no",
            "secondary_phone",
            "agent_name",
        ],
    },
    "T5": {
        "name": "Merge Accounts_Member has 2IBC accounts",
        "description": "Denial_Merge Account is not possible DPA Failed (Other Account) _Member",
        "audience": "member",
        "subject": "Update on your IndiGo BluChip merge request",
        "body": (
            "Dear {member_last_name},\n\n"
            + _CONTACT_OPENER
            + "\n\n"
            "We acknowledge your request to merge two IndiGo BluChip Accounts. "
            "After reviewing the details, we regret to inform you that the merge "
            "account request cannot be processed as the verification process for "
            "your other IndiGo BluChip Account could not be successfully completed "
            "during the security question check. To protect the security of our "
            "member accounts, it is essential that all verification steps are "
            "passed.\n\n"
            "We truly value your association with IndiGo BluChip and appreciate "
            "your understanding.\n\n"
            "If you have any questions or require further assistance, please reply "
            "to this email or contact our support team on 01246173838, and we will "
            "be happy to help.\n\n"
            "Regards,\n"
            "{agent_name}\n"
            "Member Support Team\n"
            "IndiGo BluChip"
        ),
        "fields": [
            "member_last_name",
            "primary_phone",
            "call_time",
            "call_reason",
            "agent_name",
        ],
    },
    "T6": {
        "name": "Merge Accounts_Member has 2IBC accounts",
        "description": "Merge Account not possible as Co-brand linked with another account_member",
        "audience": "member",
        "subject": "Update on your IndiGo BluChip merge request",
        "body": (
            "Dear {member_last_name},\n\n"
            + _CONTACT_OPENER
            + "\n\n"
            "We acknowledge your request to merge two IndiGo BluChip Accounts. "
            "After reviewing the details, we regret to inform you that the merge "
            "account request cannot be processed as your privileges and benefits "
            "linked to the Co Brand Credit Card {cobrand_bank_name} are associated "
            "with the other account mobile number, merging the accounts would "
            "result in discontinuation of those privileges and benefits.\n\n"
            "That said, we want to ensure you have flexibility in managing your "
            "membership. If you are comfortable with making your other account "
            "registered mobile number as the Primary account, please reply to this "
            "email. Once we receive your confirmation, our team will review the "
            "request further and guide you on the next steps.\n\n"
            "We truly value your association with IndiGo BluChip and appreciate "
            "your understanding.\n\n"
            "If you have any questions or require further assistance, please reply "
            "to this email or contact our support team, and we will be happy to "
            "help.\n\n"
            "Regards,\n"
            "{agent_name}\n"
            "Member Support Team\n"
            "IndiGo BluChip"
        ),
        "fields": [
            "member_last_name",
            "primary_phone",
            "call_time",
            "call_reason",
            "cobrand_bank_name",
            "agent_name",
        ],
    },
    "T7": {
        "name": "Merge Accounts_Member has 2IBC accounts",
        "description": "Denial_Merge Account not possible-name mismatch_Member",
        "audience": "member",
        "subject": "Update on your IndiGo BluChip merge request",
        "body": (
            "Dear {member_last_name},\n\n"
            + _CONTACT_OPENER
            + "\n\n"
            "We acknowledge your request to merge two IndiGo BluChip accounts. "
            "After reviewing the details, we regret to inform you that the merge "
            "account request cannot be processed as the names registered on both "
            "accounts do not match, the program guidelines require that account "
            "details, including the registered name, remain consistent across both "
            "accounts.\n\n"
            "We truly value your association with IndiGo BluChip and appreciate "
            "your understanding.\n\n"
            "If you have any questions or require further assistance, please reply "
            "to this email or contact our support team, and we will be happy to "
            "help.\n\n"
            "Regards,\n"
            "{agent_name}\n"
            "Member Support Team\n"
            "IndiGo BluChip"
        ),
        "fields": [
            "member_last_name",
            "primary_phone",
            "call_time",
            "call_reason",
            "agent_name",
        ],
    },
    "T8": {
        "name": "Merge Accounts_Member has 2IBC accounts",
        "description": "Denial_Merge Account not possible-DPA failed on other account_Member",
        "audience": "member",
        "subject": "Update on your IndiGo BluChip merge request",
        "body": (
            "Dear {member_last_name},\n\n"
            + _CONTACT_OPENER
            + "\n\n"
            "We acknowledge your request to merge two IndiGo BluChip Accounts. "
            "After reviewing the details, we regret to inform you that the merge "
            "account request cannot be processed as the verification process for "
            "your other IndiGo BluChip account could not be successfully completed "
            "during the security question check. To protect the security and "
            "integrity of member accounts, it is essential that all verification "
            "steps are passed.\n\n"
            "We truly value your association with IndiGo BluChip and appreciate "
            "your understanding.\n\n"
            "If you have any questions or require further assistance, please reply "
            "to this email or contact our support team, and we will be happy to "
            "help.\n\n"
            "Regards,\n"
            "{agent_name}\n"
            "Member Support Team\n"
            "IndiGo BluChip"
        ),
        "fields": [
            "member_last_name",
            "primary_phone",
            "call_time",
            "call_reason",
            "agent_name",
        ],
    },
    "T9": {
        "name": "Merge Accounts_Member has 2 IBC accounts",
        "description": "Resolution Email for successful merger of Accounts",
        "audience": "member",
        "subject": "Your IndiGo BluChip accounts have been successfully merged",
        "body": (
            "Dear {member_last_name},\n\n"
            "We are pleased to inform you that your request to merge your IndiGo "
            "BluChip accounts has been successfully completed. The IndiGo BluChips "
            "balance & related benefits (If any) from your secondary account has "
            "been transferred to your primary account {primary_membership_no}. "
            "Kindly note that this IndiGo BluChip Account {primary_membership_no} "
            "is now designated as your Primary account and cannot be merged with "
            "any other IndiGo BluChip Account in the future.\n\n"
            "Please logout and re-login into your IndiGo BluChip account using "
            "email ID {primary_email}/mobile number {primary_phone} and review "
            "your details to ensure everything is correct.\n\n"
            "If you have any questions or require further assistance, please reply "
            "to this email or contact our support team, and we will be happy to "
            "help.\n\n"
            "Regards,\n"
            "{agent_name}\n"
            "Member Support Team\n"
            "IndiGo BluChip"
        ),
        "fields": [
            "member_last_name",
            "primary_membership_no",
            "primary_email",
            "primary_phone",
            "agent_name",
        ],
    },
    "T10": {
        "name": "Merge Accounts_Member has 2 IBC accounts",
        "description": "Request to program Ops_Internal",
        "audience": "internal",
        "subject": "Action required: Execute IndiGo BluChip account merge",
        "body": (
            "Dear Team,\n\n"
            "The customer has requested to merge two IndiGo BluChip accounts into "
            "a single primary account. Verification confirms both accounts belong "
            "to the same individual, with matching name and date of birth. The "
            "request has also been raised from both registered email IDs (Details "
            "in trail mail).\n\n"
            "Account 1:\n"
            "• Membership number: {account1_membership_no}\n"
            "• Name on IndiGo BluChip Account: {account1_name}\n"
            "• IBC Balance: {account1_ibc_balance}\n\n"
            "Account 2:\n"
            "• Membership number: {account2_membership_no}\n"
            "• Name on IndiGo BluChip Account: {account2_name}\n"
            "• IBC Balance: {account2_ibc_balance}\n\n"
            "Proposed Primary Account:\n"
            "• Membership Number: {primary_membership_no}\n"
            "• Phone: {primary_phone}\n"
            "• Email: {primary_email}\n\n"
            "The member has requested transfer of the IndiGo BluChips balance from "
            "the secondary account to the primary account, followed by "
            "deactivation of the secondary account.\n\n"
            "Kindly proceed with the necessary actions and confirm once complete, "
            "or advise if any additional steps are required. Please refer to the "
            "trail mail and attachments for details.\n\n"
            "Thank you for your support.\n\n"
            "Regards,\n"
            "{agent_name}\n"
            "Member Support Team\n"
            "IndiGo BluChip"
        ),
        "fields": [
            "account1_membership_no",
            "account1_name",
            "account1_ibc_balance",
            "account2_membership_no",
            "account2_name",
            "account2_ibc_balance",
            "primary_membership_no",
            "primary_phone",
            "primary_email",
            "agent_name",
        ],
    },
}
