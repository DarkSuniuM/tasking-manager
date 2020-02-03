"""empty message

Revision ID: 7bbc01082457
Revises: 84c793a951b2
Create Date: 2020-01-29 11:19:20.113089

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "7bbc01082457"
down_revision = "84c793a951b2"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # Select all existing organisation tags from projects table
    org_tags = conn.execute("select distinct(organisation_tag) from projects")

    # Make an entry into organisation table for each tag
    # identified from projects table
    for org_tag in org_tags:
        org = org_tag[0]
        if org:
            conn.execute("insert into organisations (name) values ('" + str(org) + "')")
            select_org_id = conn.execute(
                "select id from organisations where name ='" + org + "'"
            ).fetchall()
            org_id = select_org_id[0][0]
            projects = conn.execute(
                "select id from projects where organisation_tag='" + str(org) + "'"
            )
            for project in projects:
                project_id = project[0]
                conn.execute(
                    "update projects set organisation_id="
                    + str(org_id)
                    + " where id="
                    + str(project_id)
                )


def downgrade():
    conn = op.get_bind()
    conn.execute(
        "update projects set organisation_id = null where organisation_id is not null"
    )
    conn.execute("delete from organisations where name is not null")
