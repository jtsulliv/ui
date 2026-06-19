
import difflib

def interactive_merge(original_lines, new_lines):
    # Generate line-by-line differences with ndiff
    diff = list(difflib.ndiff(original_lines, new_lines))
    final_text = []
    i = 0
    
    while i < len(diff):
        line = diff[i]
        prefix = line[:2]
        text = line[2:]

        # Unmodified line
        if prefix == '  ':
            final_text.append(text)
            i += 1
        
        # Found a deletion, insertion, or replacement
        elif prefix in ('- ', '+ ', '? '):
            print(f"\nChange detected: {line.strip()}")
            
            # Interactive prompt for the user to approve
            choice = input("Approve this change? [y/n/q]: ").strip().lower()
            
            if choice == 'q':
                print("Merge cancelled.")
                break
            elif choice == 'y':
                if prefix in ('+ ', '? '):
                    final_text.append(text)
            elif choice == 'n':
                if prefix == '- ':
                    # Keep the original if the deletion is rejected
                    final_text.append(text)
            i += 1

    return "".join(final_text)

# Example Usage
original = ["Apple\n", "Banana\n", "Cherry\n"]
updated =  ["Apple\n", "Blueberry\n", "Cherry\n"]

merged = interactive_merge(original, updated)
print("\nFinal Result:\n", merged)
