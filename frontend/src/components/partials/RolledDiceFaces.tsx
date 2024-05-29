const RolledDiceFaces = ({ user, rolledDice }: { user:string, rolledDice: string[] }) => {
    return (
        <div className="flex flex-col items-center">
            <p className="text-white text-2xl">{user} Dices</p>
            <div className="flex flex-wrap justify-center items-center outline outline-white rounded-lg">
                {rolledDice.map((face, index) => (
                    <div key={index} className="m-2 p-1 w-8 h-8 lg:w-10 lg:h-10 lg:p-2 text-center bg-nyanza text-black rounded-lg">
                        {face}
                    </div>
                ))}
            </div>
        </div>
    );
}

export default RolledDiceFaces;