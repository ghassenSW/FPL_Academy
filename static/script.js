async function CopyPriceChange(event) {
    try {
        if (event.target.tagName.toLowerCase() === 'button') {
            const id = event.target.id;
        const response = await fetch(`/get-copy-price-change?id=${id}`);
        const data = await response.json();
        const textToCopy = data.text;
        
        navigator.clipboard.writeText(textToCopy).then(() => {
            alert('Text copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });}
    } catch (error) {
        console.error('Error fetching text: ', error);
    }
}

async function CopyInjuryUpdates(event) {
    try {
        if (event.target.tagName.toLowerCase() === 'button') {
            const id = event.target.id;
        const response = await fetch(`/get-copy-injury-updates?id=${id}`);
        const data = await response.json();
        const textToCopy = data.text;
        
        navigator.clipboard.writeText(textToCopy).then(() => {
            alert('Text copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });}
    } catch (error) {
        console.error('Error fetching text: ', error);
    }
}

document.querySelectorAll('button').forEach(button => {
    if (button.parentElement && button.parentElement.id === 'button_injury') {
        button.addEventListener('click', CopyInjuryUpdates);
    }
    else if (button.parentElement && button.parentElement.id === 'button_price') {
        button.addEventListener('click', CopyPriceChange);
    }
});
