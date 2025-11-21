"""Add products table and seed initial catalog

Revision ID: 002
Revises: 001
Create Date: 2024-11-21

"""

from alembic import op
import sqlalchemy as sa
import textwrap

# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def _seed_products():
    """Insert the initial catalog inspired by data/products.yaml."""
    products_table = sa.table(
        "products",
        sa.column("slug", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("ingredients", sa.Text),
        sa.column("price", sa.Float),
        sa.column("weight_display", sa.String),
        sa.column("packaging_pieces", sa.Integer),
        sa.column("packaging_grams", sa.Integer),
        sa.column("image", sa.String),
        sa.column("is_active", sa.Boolean),
    )

    catalog = [
        {
            "slug": "pakket-klein",
            "name": "Varkensvlees Pakket",
            "description": textwrap.dedent(
                """
                Gemengd pakket met verschillende stukken van het varken. Het pakket bevat
                altijd: filetkotelet, spiering, spek en gehakt. Verder wordt het
                gevarieerd met hespelapjes, stoofvlees, hamburgers, blinde vink,
                boerenworst of chipolata.

                Alle producten zijn vacuüm verpakt.
                """
            ).strip(),
            "ingredients": None,
            "price": 17.50,
            "weight_display": "per kg",
            "packaging_pieces": 1,
            "packaging_grams": 5000,
            "image": None,
            "is_active": True,
        },
        {
            "slug": "filetkotelet",
            "name": "Filetkotelet",
            "description": "Malse filetkotelet, perfect voor op de BBQ of in de pan. Heerlijk mals en sappig. Vacuüm verpakt.",
            "ingredients": "_100% varkensvlees_",
            "price": 19.50,
            "weight_display": "per kg",
            "packaging_pieces": 2,
            "packaging_grams": 400,
            "image": None,
            "is_active": True,
        },
        {
            "slug": "spieringkotelet",
            "name": "Spieringkotelet",
            "description": "Sappige spieringkotelet met veel smaak. Ideaal voor een snelle weekavond maaltijd. Vacuüm verpakt.",
            "ingredients": None,
            "price": 19.50,
            "weight_display": "per kg",
            "packaging_pieces": 1,
            "packaging_grams": 250,
            "image": None,
            "is_active": True,
        },
        {
            "slug": "stoofvlees",
            "name": "Stoofvlees",
            "description": "Mals stoofvlees, wordt heerlijk zacht bij langzaam stoven. Perfect voor een klassieke Vlaamse stoofpot.",
            "ingredients": None,
            "price": 19.50,
            "weight_display": "per kg",
            "packaging_pieces": 1,
            "packaging_grams": 750,
            "image": None,
            "is_active": True,
        },
        {
            "slug": "spek",
            "name": "Spek",
            "description": "Vers spek met mooie vetlaag. Lekker gebakken of om gerechten mee te verrijken. Vacuüm verpakt.",
            "ingredients": None,
            "price": 17.50,
            "weight_display": "per kg",
            "packaging_pieces": 4,
            "packaging_grams": 250,
            "image": None,
            "is_active": True,
        },
        {
            "slug": "hamburger",
            "name": "Hamburger",
            "description": "Sappige hamburgers van 100% varkensvlees. Ideaal voor BBQ of in de pan. Vacuüm verpakt.",
            "ingredients": None,
            "price": 17.50,
            "weight_display": "per kg",
            "packaging_pieces": 2,
            "packaging_grams": 250,
            "image": None,
            "is_active": True,
        },
        {
            "slug": "boerenworst",
            "name": "Boerenworst",
            "description": "Verse boerenworst met authentieke kruiding. Heerlijk bij appelmoes of stamppot. Vacuüm verpakt.",
            "ingredients": None,
            "price": 17.50,
            "weight_display": "per kg",
            "packaging_pieces": 4,
            "packaging_grams": 500,
            "image": None,
            "is_active": True,
        },
        {
            "slug": "chipolata",
            "name": "Chipolata",
            "description": "Verse chipolatas, fijne worstjes vol smaak. Vacuüm verpakt.",
            "ingredients": None,
            "price": 18.00,
            "weight_display": "per kg",
            "packaging_pieces": 4,
            "packaging_grams": 500,
            "image": None,
            "is_active": True,
        },
        {
            "slug": "blinde-vink",
            "name": "Blinde Vink",
            "description": "Klassieke blinde vinken, gevuld en klaar om te bereiden. Traditioneel Vlaams gerecht. Vacuüm verpakt.",
            "ingredients": None,
            "price": 18.50,
            "weight_display": "per kg",
            "packaging_pieces": 2,
            "packaging_grams": 300,
            "image": None,
            "is_active": True,
        },
        {
            "slug": "gehakt",
            "name": "Gehakt",
            "description": "100% varkensgehakt, veelzijdig te gebruiken. Voor gehaktballen, saus of als basis voor vele gerechten.",
            "ingredients": None,
            "price": 15.00,
            "weight_display": "per kg",
            "packaging_pieces": 1,
            "packaging_grams": 500,
            "image": None,
            "is_active": True,
        },
        {
            "slug": "zwarte-pens",
            "name": "Zwarte Pens",
            "description": "Traditionele zwarte pens, een streekproduct met veel smaak. Lekker gebakken met appelmoes. Vacuüm verpakt.",
            "ingredients": None,
            "price": 4.50,
            "weight_display": "per 2 stuks",
            "packaging_pieces": 2,
            "packaging_grams": 300,
            "image": None,
            "is_active": True,
        },
        {
            "slug": "varkenshaas",
            "name": "Varkenshaas",
            "description": "Malse varkenshaas, het meest mals stuk vlees. Perfect voor een feestelijk diner. Vacuüm verpakt.",
            "ingredients": None,
            "price": 26.00,
            "weight_display": "per kg",
            "packaging_pieces": 1,
            "packaging_grams": 500,
            "image": None,
            "is_active": True,
        },
        {
            "slug": "hespengebraad",
            "name": "Hespengebraad",
            "description": "Sappig hespengebraad met mooie vetverdeling. Ideaal voor in de oven of slowcooker. Vacuüm verpakt.",
            "ingredients": None,
            "price": 21.00,
            "weight_display": "per kg",
            "packaging_pieces": 1,
            "packaging_grams": 1000,
            "image": None,
            "is_active": True,
        },
        {
            "slug": "carre-gebraad",
            "name": "Carré Gebraad",
            "description": "Mals carré gebraad. Een indrukwekkend gebraad voor zondag of feestdagen. Vacuüm verpakt.",
            "ingredients": None,
            "price": 21.00,
            "weight_display": "per kg",
            "packaging_pieces": 1,
            "packaging_grams": 1000,
            "image": None,
            "is_active": True,
        },
        {
            "slug": "varkenspoot",
            "name": "Varkenspoten",
            "description": "Varkenspoten, ideaal voor in de bouillon of om te confijten. Een delicatesse voor echte fijnproevers.",
            "ingredients": None,
            "price": 3.00,
            "weight_display": "per 2 stuks",
            "packaging_pieces": 2,
            "packaging_grams": 800,
            "image": None,
            "is_active": True,
        },
    ]

    op.bulk_insert(products_table, catalog)


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("ingredients", sa.Text(), nullable=True),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("weight_display", sa.String(length=100), nullable=False),
        sa.Column("packaging_pieces", sa.Integer(), nullable=True),
        sa.Column("packaging_grams", sa.Integer(), nullable=True),
        sa.Column("image", sa.String(length=255), nullable=True),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_products_id", "products", ["id"])
    op.create_index("ix_products_slug", "products", ["slug"], unique=True)
    op.create_index("ix_products_is_active", "products", ["is_active"])

    _seed_products()


def downgrade() -> None:
    op.drop_index("ix_products_is_active", table_name="products")
    op.drop_index("ix_products_slug", table_name="products")
    op.drop_index("ix_products_id", table_name="products")
    op.drop_table("products")
