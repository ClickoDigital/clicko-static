#!/usr/bin/env python3
"""
Spam Protection Script for Clicko Digital Website
Applies comprehensive spam protection to all forms across the site.
"""

import os
import re
import glob
from pathlib import Path

def add_spam_protection_to_form(form_content):
    """Add spam protection fields and validation to a form"""
    
    # Check if spam protection is already added
    if 'form_timestamp' in form_content:
        return form_content
    
    # Find the form tag and add spam protection fields
    form_pattern = r'(<form[^>]*>)'
    
    def add_protection_fields(match):
        form_tag = match.group(1)
        
        spam_protection_html = f"""
{form_tag}
			
				<!-- Spam Protection Fields -->
				<div style="display: none !important; visibility: hidden; opacity: 0; position: absolute; left: -9999px;" aria-hidden="true">
					<label for="website_url">Website URL (leave blank):</label>
					<input type="text" id="website_url" name="website_url" tabindex="-1" autocomplete="off">
					
					<label for="phone_alt">Phone Alt (leave blank):</label>
					<input type="text" id="phone_alt" name="phone_alt" tabindex="-1" autocomplete="off">
					
					<label for="company_name">Company Name (leave blank):</label>
					<input type="text" id="company_name" name="company_name" tabindex="-1" autocomplete="off">
				</div>
				
				<!-- Time-based validation -->
				<input type="hidden" name="form_timestamp" id="form_timestamp" value="">
				<input type="hidden" name="form_token" id="form_token" value="">
				
"""
        return spam_protection_html
    
    return re.sub(form_pattern, add_protection_fields, form_content)

def add_spam_protection_script(content):
    """Add spam protection JavaScript to the page"""
    
    # Check if spam protection script is already added
    if 'Spam Protection Script' in content:
        return content
    
    spam_protection_script = """
<script>
// Spam Protection Script
document.addEventListener('DOMContentLoaded', function() {
    // Initialize form timestamps and tokens
    const forms = document.querySelectorAll('form');
    
    forms.forEach(function(form) {
        // Set form timestamp when page loads
        const timestampField = form.querySelector('input[name="form_timestamp"]');
        if (timestampField) {
            timestampField.value = Date.now();
        }
        
        // Generate form token
        const tokenField = form.querySelector('input[name="form_token"]');
        if (tokenField) {
            tokenField.value = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
        }
        
        // Add form submission validation
        form.addEventListener('submit', function(e) {
            // Check honeypot fields
            const honeypotFields = form.querySelectorAll('input[name="website_url"], input[name="phone_alt"], input[name="company_name"]');
            let honeypotFilled = false;
            
            honeypotFields.forEach(function(field) {
                if (field.value.trim() !== '') {
                    honeypotFilled = true;
                }
            });
            
            if (honeypotFilled) {
                e.preventDefault();
                console.log('Spam detected: Honeypot fields filled');
                return false;
            }
            
            // Check time-based validation (minimum 3 seconds)
            const timestampField = form.querySelector('input[name="form_timestamp"]');
            if (timestampField) {
                const formStartTime = parseInt(timestampField.value);
                const currentTime = Date.now();
                const timeDiff = currentTime - formStartTime;
                
                if (timeDiff < 3000) { // Less than 3 seconds
                    e.preventDefault();
                    console.log('Spam detected: Form submitted too quickly');
                    alert('Please take a moment to review your information before submitting.');
                    return false;
                }
            }
            
            // Check for suspicious patterns in form data
            const nameField = form.querySelector('input[name*="name"], input[name*="Name"]');
            const emailField = form.querySelector('input[type="email"], input[name*="email"], input[name*="Email"]');
            const messageField = form.querySelector('textarea[name*="message"], textarea[name*="Message"]');
            
            if (nameField && emailField && messageField) {
                const name = nameField.value.toLowerCase();
                const email = emailField.value.toLowerCase();
                const message = messageField.value.toLowerCase();
                
                // Check for spam keywords
                const spamKeywords = ['viagra', 'casino', 'lottery', 'winner', 'congratulations', 'click here', 'free money', 'bitcoin', 'crypto', 'investment', 'loan', 'debt', 'credit', 'make money', 'work from home', 'get rich', 'earn money', 'online casino', 'gambling', 'pills', 'pharmacy', 'weight loss', 'diet', 'supplements'];
                
                let spamDetected = false;
                spamKeywords.forEach(function(keyword) {
                    if (name.includes(keyword) || email.includes(keyword) || message.includes(keyword)) {
                        spamDetected = true;
                    }
                });
                
                if (spamDetected) {
                    e.preventDefault();
                    console.log('Spam detected: Suspicious keywords found');
                    alert('Your message contains suspicious content. Please review and try again.');
                    return false;
                }
                
                // Check for excessive repetition
                if (message.length > 0) {
                    const words = message.split(' ');
                    const wordCount = {};
                    words.forEach(function(word) {
                        if (word.length > 3) {
                            wordCount[word] = (wordCount[word] || 0) + 1;
                        }
                    });
                    
                    let maxRepetition = 0;
                    Object.values(wordCount).forEach(function(count) {
                        if (count > maxRepetition) {
                            maxRepetition = count;
                        }
                    });
                    
                    if (maxRepetition > 5) {
                        e.preventDefault();
                        console.log('Spam detected: Excessive word repetition');
                        alert('Your message contains excessive repetition. Please review and try again.');
                        return false;
                    }
                }
            }
            
            // Update timestamp on successful validation
            if (timestampField) {
                timestampField.value = Date.now();
            }
        });
    });
});
</script>"""
    
    # Insert before closing body tag
    if '</body>' in content:
        content = content.replace('</body>', f'{spam_protection_script}\n</body>')
    elif '</html>' in content:
        content = content.replace('</html>', f'{spam_protection_script}\n</html>')
    else:
        content += spam_protection_script
    
    return content

def process_html_file(file_path):
    """Process a single HTML file to add spam protection"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Check if file contains forms
        if '<form' not in content:
            return False
        
        # Add spam protection to forms
        content = add_spam_protection_to_form(content)
        
        # Add spam protection script
        content = add_spam_protection_script(content)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to apply spam protection to all HTML files"""
    
    # Get all HTML files in clickodigital.com directory
    html_files = glob.glob('clickodigital.com/**/*.html', recursive=True)
    
    print(f"Found {len(html_files)} HTML files to process...")
    
    processed_count = 0
    forms_found_count = 0
    
    for file_path in html_files:
        # Skip backup files
        if '.php_fix_backup' in file_path:
            continue
            
        print(f"Processing: {file_path}")
        
        # Check if file has forms
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '<form' in content:
                forms_found_count += 1
                if process_html_file(file_path):
                    processed_count += 1
                    print(f"  ✅ Added spam protection")
                else:
                    print(f"  ⚠️  Already has spam protection or no changes needed")
            else:
                print(f"  ➖ No forms found")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\n📊 Summary:")
    print(f"  Total HTML files: {len(html_files)}")
    print(f"  Files with forms: {forms_found_count}")
    print(f"  Files processed: {processed_count}")
    print(f"  Files skipped: {len(html_files) - processed_count}")

if __name__ == "__main__":
    main()
