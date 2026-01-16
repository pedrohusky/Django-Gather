// BFS pathfinding algorithm
function bfs(start, end, blocked, maxAttempts = 10000) {
    const endKey = `${end[0]}, ${end[1]}`;
    if (blocked.has(endKey)) {
        return null;
    }

    const directions = [
        [0, 1], [1, 0], [0, -1], [-1, 0]
    ];

    const queue = [[start, [start]]];
    const visited = new Set(blocked);
    visited.add(`${start[0]}, ${start[1]}`);

    let attempts = 0;

    while (queue.length > 0) {
        if (attempts >= maxAttempts) {
            return null;
        }
        attempts++;

        const [currentPos, path] = queue.shift();
        const [x, y] = currentPos;

        if (x === end[0] && y === end[1]) {
            return path.slice(1);
        }

        for (const [dx, dy] of directions) {
            const nextPos = [x + dx, y + dy];
            const nextPosStr = `${nextPos[0]}, ${nextPos[1]}`;
            if (!visited.has(nextPosStr)) {
                visited.add(nextPosStr);
                queue.push([nextPos, path.concat([nextPos])]);
            }
        }
    }

    return null;
}

window.bfs = bfs;
