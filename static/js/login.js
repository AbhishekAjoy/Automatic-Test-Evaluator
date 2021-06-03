function checkFormEntry()
{
	document.getElementById("errorMessage").innerHTML="";
	document.getElementById("successMessage").innerHTML="";
	
	var errors="";
	if(document.getElementById("username").value.length<5)
	{
		errors="The username must be at least 5 Character.<br />";
	}
	
	if(document.getElementById("password").value.length<8)
	{
		alert("Please Type Correct 8 digit Password");
	}
	

	if(errors!="")
	{
		document.getElementById("errorMessage").innerHTML=errors;
	}
	else{
		window.location.href="index.html";
		alert("You have Successfully logged in.")
	}
	return false; 
}

document.getElementById("form1").onsubmit=checkFormEntry;