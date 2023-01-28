
const name = document.getElementById('name-form');
const password = document.getElementById('password-form');



function isValid(){
     const nameValue = String(name.value);
     const passwordValue1 = String(password.value);
     const passwordValue2 = String(password.value);
     const passwordValue3 = String(password.value);
     const passwordValue4 = String(password.value);
     const passwordValue5 = String(password.value);
     
     
    containsWhitespace(nameValue);
    isEmpty(nameValue);
    isValidLen(passwordValue1);
    containsUpper(passwordValue2);
    containsLower(passwordValue3);
    containsDigit(passwordValue4);
    containsLetter(passwordValue5);
}

function isEmpty(inputName){
     if(inputName.length === 0)
     {
         //alert('Username Error: Username cannot be empty.');
         document.getElementById('usernameEmptyError').innerHTML = 'Username Error: Username cannot be empty.';
     }
     
}

function containsWhitespace(inputName)
{
    
    //document.getElementById('usernameWhitespaceError').innerHTML = 'Username Error: Username cannot contain whitespace.';

    
    
     for(var i = 0; i < inputName.length; i++)
     {
         if(inputName[i] === ' ')
         {
            document.getElementById('usernameWhitespaceError').innerHTML = 'Username Error: Username cannot contain whitespace.';
         }
     }
     

}
function isValidLen(inputPassword){
     if(inputPassword.length < 3)
     {
         //alert('Password should contain at least 3 characters.');
         document.getElementById('passwordLenError').innerHTML = 'Password Error: Password should contain at least 3 characters.';
     }
     
     if(inputPassword.length > 20)
     {
        //alert('Password should contain at most 20 characters.');
        document.getElementById('passwordLenError').innerHTML = 'Password Error: Password should contain at most 20 characters.';
     }
}



function containsUpper(inputPassword){
     var Upper = 0;

     for(var i = 0; i < inputPassword.length; i++)
     {
        var temp1 = inputPassword[i];
        
        if(temp1.toUpperCase() === temp1)
        {
           Upper = 1;
        }
     }
     
     if(Upper === 0)
     {
        //alert('Password should contain at least one upper case character.');
        document.getElementById('passwordUpperError').innerHTML = 'Password Error: Password should contain at least one upper case character.';
     }
}

function containsLower(inputPassword){
    
     var Lower = 0;
     for(var i = 0; i < inputPassword.length; i++)
     {
       
        var temp2 = inputPassword[i];

        if(temp2.toLowerCase() === temp2)
        {
           Lower = 1;
        }
     }
     if(Lower === 0)
     {
        //alert('Password should contain at least one lower case character.');
        document.getElementById('passwordLowerError').innerHTML = 'Password Error: Password should contain at least one lower case character.';
     }
    
}

function containsDigit(inputPassword){
    
     if(inputPassword.length === 0)
     {
       document.getElementById('passwordDigitError').innerHTML = 'Password Error: Password should contain at least one digit.';
     }
     
    else if(!/\d/.test(inputPassword))
     {
        //alert('Password should contain at least one digit.');
        document.getElementById('passwordDigitError').innerHTML = 'Password Error: Password should contain at least one digit.';
     }
    
}

function containsLetter(inputPassword){
    
     if(inputPassword.length === 0)
     {
       document.getElementById('passwordLetterError').innerHTML = 'Password Error: Password should contain at least one letter.';
     }
     
    else if(!/[a-zA-Z]/g.test(inputPassword))
     {
        //alert('Password should contain at least one digit.');
        document.getElementById('passwordLetterError').innerHTML = 'Password Error: Password should contain at least one letter.';
     }
    
}