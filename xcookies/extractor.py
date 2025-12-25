"""Core cookie extraction logic using Playwright."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

from playwright.sync_api import sync_playwright, Browser, TimeoutError as PlaywrightTimeout


@dataclass
class AccountCredentials:
    """Input credentials for an X account."""
    username: str
    auth_token: str


@dataclass
class ExtractedCookies:
    """Extracted cookies from successful session."""
    username: str
    auth_token: str
    ct0: str
    twid: Optional[str] = None
    guest_id: Optional[str] = None


class CookieExtractor:
    """Extracts auth cookies from X accounts by injecting auth_token."""
    
    def extract_single(self, creds: AccountCredentials) -> Optional[ExtractedCookies]:
        """Extract cookies from a single account."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                return self._inject_and_extract(browser, creds)
            finally:
                browser.close()
    
    def _inject_and_extract(
        self, 
        browser: Browser, 
        creds: AccountCredentials
    ) -> Optional[ExtractedCookies]:
        """Inject auth_token and extract all cookies."""
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        )
        
        try:
            # Inject auth_token cookie
            context.add_cookies([{
                "name": "auth_token",
                "value": creds.auth_token,
                "domain": ".x.com",
                "path": "/",
                "httpOnly": True,
                "secure": True,
                "sameSite": "None",
            }])
            
            page = context.new_page()
            
            # Navigate to X.com
            try:
                page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=60000)
            except PlaywrightTimeout:
                pass  # Continue anyway
            
            # Wait for cookies to be set
            time.sleep(5)
            
            # Check if redirected to login (invalid token)
            if "/login" in page.url or "/i/flow/login" in page.url:
                return None
            
            # Extract cookies
            return self._extract_cookies(context, creds)
            
        except Exception:
            return None
        finally:
            context.close()
    
    def _extract_cookies(self, context, creds: AccountCredentials) -> Optional[ExtractedCookies]:
        """Extract cookies from browser context."""
        cookies = {c["name"]: c["value"] for c in context.cookies()}
        
        ct0 = cookies.get("ct0")
        if not ct0:
            return None
        
        return ExtractedCookies(
            username=creds.username,
            auth_token=cookies.get("auth_token", creds.auth_token),
            ct0=ct0,
            twid=cookies.get("twid"),
            guest_id=cookies.get("guest_id"),
        )

