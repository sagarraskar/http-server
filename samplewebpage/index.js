const btn = document.querySelector("button")

btn.addEventListener('click', ()=>{
    const output = document.querySelector(".output")
    const input = document.querySelector(".container input").value

    if (input.split("").every((digit)=>{
        return digit == '0' || digit == '1'
    }))
    {
        output.textContent = Bin2Dec(input)
    }
    else{
        output.textContent = "Invalid Binary Number"
    }
})

const Bin2Dec = (input)=>{
	return parseInt(input, 2)
}
