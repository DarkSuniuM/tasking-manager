"""empty message

Revision ID: 7bbc01082457
Revises: 84c793a951b2
Create Date: 2020-01-29 11:19:20.113089

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7bbc01082457"
down_revision = "c40e1fdf6b70"
branch_labels = None
depends_on = None


def upgrade():
    orgs_map = {
        "Médecins Sans Frontières": "MSF",
        "UNHCR": "United Nations",
        "UNICEF": "United Nations",
        "UNOCH": "United Nations",
        "UN Mappers": "United Nations",
        "UN-Habitat": "United Nations",
        "UNDP Tajikistan": "United Nations",
        "kaart": "Kaart",
        "#GrabPH": "Grab",
        "#maptimemelbourne": "MapTime",
        "#osmgeoweek": "Missing Maps",
        "Clinton Health Access Initiative (CHAI)": "Clinton Health Access Initiative",
        "KLL": "Kathmandu Living Labs",
        "NASA Disasters Program": "NASA",
        "#PublicLabMongolia": "Public Lab Mongolia",
        "akros": "Akros",
        "#akros": "Akros",
        "#Akros": "Akros",
        "CDEMA": "Caribbean Disaster Emergency Management Agency",
        "INTEGRATION": "INTEGRATION Consulting Group",
        "#PADF": "Pan American Development Foundation",
        "PADF": "Pan American Development Foundation",
        "WFP": "World Food Programme",
        "COOPI -Concern Worldwide": "Concern Worldwide",
        "Liberia Water and Sewer Corporation and OSM": "LISGIS",
        "HOTOSM": "HOT",
        "#HOT": "HOT",
        "#HOT#Jumeme#Missing Maps": "HOT",
        "#HOTOSM #KCCA": "HOT",
        "Humanitarian OpenStreetMap Team Indonesia": "HOT Indonesia",
        "Ramani Huria": "HOT Tanzania",
        "#Data Zetu": "HOT Tanzania",
        "#OMDTZ": "HOT Tanzania",
        "Kampala Capital City Authority": "HOT Uganda",
        "#YouthMappers": "YouthMappers",
        "Kenyatta University  GIS Club": "YouthMappers",
        "UMaT YouthMappers": "YouthMappers",
        "UniqueMappers Network": "YouthMappers",
        "Universidad de Antioquia": "YouthMappers",
        "#UniBonn": "YouthMappers",
        "UniqueMappersTeam": "YouthMappers",
        "Warwick University": "YouthMappers",
        "WarwickUni": "YouthMappers",
        "Australian Red Cross": "IFRC",
        "Austrian Red Cross": "IFRC",
        "Kenya Red Cross": "IFRC",
        "Nepal Red Cross Society": "IFRC",
        "Cruz Roja Española": "American Red Cross",
        "Red Cross Red Crescent Climate Centre": "American Red Cross",
        "GermanRedCross": "German Red Cross",
        "CrisisMappers JAPAN": "Crisis Mappers Japan",
        "MapLesotho": "Map Lesotho",
        "#MapLesotho": "Map Lesotho",
        "Albanian OpenStreetMap Community": "OSM Albania",
        "Bangladesh Humanitarian OpenStreetMap Operations Team (BHOOT)": "OSM Bangladesh",
        "OSM-BD": "OSM Bangladesh",
        "OSM-BF": "OSM Burkina Faso",
        "OpenBurkina": "OSM Burkina Faso",
        "OpenStreetMap Cameroon": "OSM Cameroon",
        "OpenStreetMapCo": "OSM Colombia",
        "#OpenStreetMapCo": "OSM Colombia",
        "OSM-CD": "OSM Congo",
        "OSM-IN": "OSM India",
        "iLab Liberia and OSM Liberia": "OSM Liberia",
        "#iLabLiberia": "OSM Liberia",
        "iLab_OSM-Liberia": "OSM Liberia",
        "OpenStreetMap Madagascar": "OSM Madagascar",
        "OSM-MX": "OSM Mexico",
        "OSM-PE": "OSM Peru",
        "OSM Perú": "OSM Peru",
        "OSM-PH": "OSM Philippines",
        "MapPH": "OSM Philippines",
        "OSMph": "OSM Philippines",
        "OSM-Somalia": "OSM Somalia",
        "OpenStreetMap South Sudan": "OSM South Sudan",
        "OSM-SE": "OSM Sweden",
        "OSM-UA": "OSM Ukraine",
        "OSM-ZWE": "OSM Zimbabwe",
    }
    org_managers = {}
    orgs_inserted = []
    conn = op.get_bind()

    # Select all existing distinct organisation tags from projects table
    org_tags = conn.execute("select distinct(organisation_tag) from projects")
    total_orgs = org_tags.rowcount
    count = 0
    for org_tag in org_tags:
        count = count + 1
        original_org_name = str(org_tag[0])
        if len(original_org_name) > 1:
            mapped_org = ""
            # Check if there is a mapping for the org - O(1) operation
            if original_org_name in orgs_map:
                mapped_org = orgs_map[original_org_name]
            else:
                mapped_org = original_org_name
            # Create new organisation only if it has not been inserted earlier
            if (mapped_org) and (mapped_org not in orgs_inserted):
                conn.execute(
                    "insert into organisations (name) values ('" + mapped_org + "')"
                )
            # Fetch organisation ID after the insert
            select_org_id = conn.execute(
                "select id from organisations where name ='" + mapped_org + "'"
            ).fetchall()
            org_id = str(select_org_id[0][0])
            # Identify projects related to the org name
            projects = conn.execute(
                "select id, author_id from projects where organisation_tag='"
                + original_org_name
                + "'"
            )
            org_manager = None
            for project_id, author_id in projects:
                conn.execute(
                    "update projects set organisation_id="
                    + org_id
                    + " where id="
                    + str(project_id)
                )
                # Capture the first author ID for the organisation
                if not org_manager:
                    org_manager = str(author_id)
                    # Check if organisation has already a manager linked to it
                    if mapped_org not in org_managers:
                        org_managers[mapped_org] = org_manager
                        conn.execute(
                            "insert into organisation_managers \
                            (organisation_id,user_id) \
                            values("
                            + org_id
                            + ","
                            + org_manager
                            + ")"
                        )

            orgs_inserted.append(mapped_org)
        if count == total_orgs:
            op.drop_column("projects", "organisation_tag")


def downgrade():
    conn = op.get_bind()
    op.add_column("projects", sa.Column("organisation_tag", sa.String(), nullable=True))
    # Remove all mappings made
    org_ids = conn.execute("select id, name from organisations")
    for org_id, org_name in org_ids:
        projects = conne.execute(
            "select id from projects where organisation_id=" + org_id
        )
        for project in projects:
            conn.execute(
                "update projects set organisation_tag="
                + str(org_name)
                + "where organisation_id="
                + str(org_id)
            )
    conn.execute("delete from organisation_managers where organisation_id is not null")
    conn.execute(
        "update projects set organisation_id = null where organisation_id is not null"
    )
    conn.execute("delete from organisations where name is not null")
