"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List

# Web3 Dapp discovery platform schemas

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Display name")
    wallet_address: Optional[str] = Field(None, description="EVM wallet address or other chain address")
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")

class Dapp(BaseModel):
    """A decentralized application listed on the platform"""
    name: str = Field(..., description="Project name")
    tagline: str = Field(..., description="Short one-line description")
    description: Optional[str] = Field(None, description="Longer description of the project")
    website: Optional[HttpUrl] = Field(None, description="Project website")
    twitter: Optional[str] = Field(None, description="Twitter/X handle or link")
    github: Optional[str] = Field(None, description="GitHub repo link")
    category: Optional[str] = Field(None, description="Category like DeFi, NFT, Tooling, Infra, Gaming")
    chains: List[str] = Field(default_factory=list, description="Supported chains")
    tags: List[str] = Field(default_factory=list, description="Extra tags")
    logo_url: Optional[str] = Field(None, description="Logo image URL")
    banner_url: Optional[str] = Field(None, description="Cover image URL")
    submitter_name: Optional[str] = Field(None, description="Name of submitter")
    submitter_wallet: Optional[str] = Field(None, description="Submitter wallet address")
    votes: int = Field(0, ge=0, description="Upvote count")

class Comment(BaseModel):
    """Comments on a Dapp"""
    dapp_id: str = Field(..., description="Related dapp id")
    author_name: Optional[str] = Field(None, description="Commenter name")
    author_wallet: Optional[str] = Field(None, description="Commenter wallet address")
    content: str = Field(..., min_length=1, max_length=1000, description="Comment text")

# Example schemas kept for reference
class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
