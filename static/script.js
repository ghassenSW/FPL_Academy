async function CopyPriceChange() {
    try {
        // Fetch text from the backend API
        const response = await fetch('/get-copy-price-change');
        const data = await response.json();
        const textToCopy = data.text;
        
        // Copy the text to clipboard
        navigator.clipboard.writeText(textToCopy).then(() => {
            alert('Text copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    } catch (error) {
        console.error('Error fetching text: ', error);
    }
}

async function CopyInjuryUpdates(event) {
    try {
        if (event.target.tagName.toLowerCase() === 'button') {
            const id = event.target.id;
        console.log(id)
        const response = await fetch(`/get-copy-injury-updates?id=${id}`);
        const data = await response.json();
        const textToCopy = data.text;
        
        navigator.clipboard.writeText(textToCopy).then(() => {
            alert('Text copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    }
    } catch (error) {
        console.error('Error fetching text: ', error);
    }
}

const price_change=document.getElementById('copy_price_change')
if (price_change)
    price_change.addEventListener('click', CopyPriceChange);


document.querySelectorAll('button').forEach(button => {
    button.addEventListener('click', CopyInjuryUpdates);
});